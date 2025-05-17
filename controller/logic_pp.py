import random
from controller.backends import GPTBackend, ClaudeBackend, LLMBackend, GeminiBackend
from memory.memory_manager import MemoryManager
from prompts.main_prompt import intro_prompt
from music.song_provider import SongProvider
import xml.etree.ElementTree as ET
from controller.interpreter import Interpreter
from controller.formatter import Formatter
from constants import MESSAGE_SNAPSHOT_FILE, CONFIG_FILE
from controller.message_streamer import (
    MessageStreamer,
    TAG_USER_INPUT,
    TAG_ASSISTANT,
    TAG_SYSTEM,
    TAG_SYSTEM_OUTPUT,
    TAG_SYSTEM_INTERNAL,
    TAG_ACTION_RESULTS,
)
import logging
import os
from datetime import datetime
import json
# from config import config as basic_config
# from configs.config_conceptual import config as basic_config
from configs.config_kivsee import config as basic_config
from animation.animation_manager import AnimationManager
from controller.actions import (ActionRegistry, UpdateAnimationAction,
                                GetAnimationAction, AddToMemoryAction,
                                InformUserAction, AskUserAction)
from schemes.main_schema import MainSchema
from typing import Dict, Any
import threading


class LogicPlusPlus:

    def __init__(self, snapshot_dir=None):
        """Initialize the LogicPlusPlus, optionally loading from a snapshot."""
        self.logger = logging.getLogger("LogicPlusPPlusLogger")
        self._pending_memory = None
        self.msgs = MessageStreamer()
        self.msgs.clear_control_flags(
        )  # Ensure control flags are cleared on initialization
        self.song_provider = SongProvider()
        self.backends = {}
        self._is_processing = False
        self._processing_lock = threading.Lock()

        # Initialize action registry
        self.action_registry = ActionRegistry()

        if snapshot_dir is not None:
            try:
                self._load_from_snapshot(snapshot_dir)
            except Exception as e:
                self.logger.error(
                    f"Failed to load snapshot from {snapshot_dir}: {e}")
                raise RuntimeError(
                    f"Failed to load snapshot from {snapshot_dir}: {e}")
        else:
            # Default initialization if no snapshot is provided
            self.config = basic_config
            self.selected_framework = self.config.get("framework", None)
            self.animation_manager = AnimationManager(self.selected_framework,
                                                      self.msgs)

        # Get the framework's schema and create the main schema
        framework_schema = self.animation_manager.get_response_object()
        self.response_schema = MainSchema.with_framework_schema(
            framework_schema)

        # Register available actions
        self._initialize_backends()
        self.memory_manager = MemoryManager(self.selected_framework)
        # Shared initialization logic
        self.selected_backend = self.config.get("selected_backend", None)
        self.response_manager = Interpreter(self.animation_manager,
                                            config=self.config)
        self.formatter = Formatter(self.msgs, self.animation_manager,
                                   self.memory_manager, self.song_provider,
                                   self.config)

        self._register_actions()

    def _register_actions(self):
        """Register all available actions"""
        self.action_registry.register_action(
            "update_animation", UpdateAnimationAction(self.animation_manager))
        self.action_registry.register_action(
            "get_animation", GetAnimationAction(self.animation_manager))
        self.action_registry.register_action(
            "add_to_memory", AddToMemoryAction(self.memory_manager))
        self.action_registry.register_action("inform_user", InformUserAction())
        self.action_registry.register_action("ask_user", AskUserAction())

    def shutdown(self, shutdown_snapshot_dir=None):
        if not shutdown_snapshot_dir:
            timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
            shutdown_snapshot_dir = os.path.join(
                self.msgs.snapshots_dir,
                f"{timestamp}_{self.selected_framework}_{self.selected_backend}"
            )
            os.makedirs(shutdown_snapshot_dir, exist_ok=True)

        # Save configuration
        snapshot_config_file = os.path.join(shutdown_snapshot_dir, CONFIG_FILE)
        with open(snapshot_config_file, "w") as file:
            json.dump(self.config, file, indent=4)

        animation_suffix = self.animation_manager.get_suffix()

        # Save all animations using the new method
        self.animation_manager.save_all_animations(shutdown_snapshot_dir,
                                                   animation_suffix)

        # Save messages to messages.json
        messages_json_file = os.path.join(shutdown_snapshot_dir,
                                          MESSAGE_SNAPSHOT_FILE)
        with open(messages_json_file, "w") as file:
            json.dump(self.msgs.messages, file,
                      indent=4)  # Save only the messages data

        # Save memory
        self.memory_manager.shutdown()

        # Finalize the msgs
        self.msgs.finalize()

        return (f"Snapshot saved: {shutdown_snapshot_dir}.")

    def get_visible_chat(self):
        """Retrieve all visible chat messages from the message_streamer, including their tags/labels."""
        return [(message['timestamp'], message['content'], message['tag'])
                for message in self.msgs.messages
                if message['visible'] and 'timestamp' in message]

    def get_chat_history(self):
        """Retrieve all chat messages, including invisible ones, with visibility and context flags."""
        chat_history = []
        for message in self.msgs.messages:
            if message['visible']:
                chat_history.append(
                    (message['timestamp'], message['content'], message['tag'],
                     message['visible'], message['context']))
            else:
                content_trimmed = message['content'][:30] + "..."
                chat_history.append(
                    (message['timestamp'],
                     f"{message['tag']} {content_trimmed}", message['tag'],
                     message['visible'], message['context']))
        return chat_history

    def _load_from_snapshot(self, snapshot_dir):
        if not os.path.exists(snapshot_dir):
            raise FileNotFoundError(
                f"Snapshot directory '{snapshot_dir}' does not exist.")

        # Check required files
        required_files = [MESSAGE_SNAPSHOT_FILE, CONFIG_FILE]
        for file_name in required_files:
            if not os.path.exists(os.path.join(snapshot_dir, file_name)):
                error_msg = f"Required file '{file_name}' is missing in the snapshot directory."
                raise FileNotFoundError(error_msg)

        animations_dir = os.path.join(snapshot_dir, "animations")
        if not os.path.exists(animations_dir):
            raise FileNotFoundError(
                "Animations directory is missing in the snapshot directory.")

        # Load messages
        messages_snapshot_file = os.path.join(snapshot_dir,
                                              MESSAGE_SNAPSHOT_FILE)
        try:
            self.msgs.load(messages_snapshot_file)
        except Exception as e:
            self.logger.error(f"Error loading messages: {e}")
            raise ValueError(f"Error loading messages: {e}")

        # Load configuration
        snapshot_config_file = os.path.join(snapshot_dir, CONFIG_FILE)
        try:
            with open(snapshot_config_file, "r") as file:
                self.config = json.load(file)
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            raise ValueError(f"Error loading configuration: {e}")

        # Load animations
        self.selected_framework = self.config.get("framework", None)
        self.animation_manager = AnimationManager(self.selected_framework,
                                                  self.msgs)
        try:
            animations = []
            for animation_file in sorted(os.listdir(animations_dir)):
                animation_path = os.path.join(animations_dir, animation_file)
                with open(animation_path, "r") as file:
                    animations.append(file.read())
            self.animation_manager.load_sequences(animations)
        except Exception as e:
            self.logger.error(f"Error loading animations: {e}")
            raise ValueError(f"Error loading animations: {e}")

        self.logger.info(f"Snapshot loaded successfully from {snapshot_dir}.")

    def _initialize_backends(self):
        backend_mapping = {
            "GPT": GPTBackend,
            "Claude": ClaudeBackend,
            "Gemini": GeminiBackend,
        }
        for backend_name, backend_class in backend_mapping.items():
            self.register_backend(
                backend_class(name=backend_name,
                              response_schema_obj=self.response_schema,
                              config=self.config))

    def register_backend(self, backend):
        if not isinstance(backend, LLMBackend):
            raise TypeError("backend must be an instance of LLMBackend.")
        self.backends[backend.name] = backend

    def select_backend(self):
        if not self.backends:
            raise ValueError("No backends available.")

        if self.selected_backend:
            selected_backend = self.backends.get(self.selected_backend)
            if selected_backend:
                return selected_backend

            self.logger.warning(
                f"Warning: Selected backend '{self.selected_backend}' not found, choosing randomly."
            )

        return random.choice(list(self.backends.values()))

    def is_processing(self):
        """Check if the backend is currently processing a request."""
        return self._is_processing

    def communicate(self, user_input):
        """Thread-safe communication with the backend."""
        with self._processing_lock:
            if self._is_processing:
                self.msgs.add_visible(
                    "system",
                    "Still processing previous request. Please wait.",
                    context=False)
                return

            self._is_processing = True
            try:
                self._communicate_internal(user_input)
            finally:
                self._is_processing = False

    def add_user_input_to_chat(self, user_input):
        self.msgs.add_visible(TAG_USER_INPUT, user_input, context=True)

    def _communicate_internal(self, user_input):
        """Internal communication method that contains the original communicate logic."""
        if self._pending_memory:
            result = self.handle_memory_approval(user_input)
            self.msgs.add_visible(TAG_SYSTEM_OUTPUT, result, context=False)
            return

        backend = self.select_backend()

        messages = self.formatter.build_messages()

        try:
            model_response = backend.generate_response(messages)
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.msgs.add_visible(TAG_SYSTEM, error_msg, context=False)
            return

        # Combine reasoning and action plan into a single message
        response_message = ""
        response_message += "Reasoning:\n" + model_response.reasoning
        if model_response.actions_plan:
            response_message += "\n\nActions plan:\n" + model_response.actions_plan
        if model_response.action:
            response_message += "\n\nI will execute action:\n" + model_response.action.name
        else:
            response_message += "\n\nNo action to execute.\n"

        self.msgs.add_visible(TAG_ASSISTANT, response_message, context=True)

        # Execute single action for this turn and handle its result
        result = self.action_registry.execute_action(
            model_response.action.name, model_response.action.params)

        if result["status"] == "error":
            error_msg = f"Error executing action {model_response.action.name}: {result['message']}"
            self.msgs.add_visible(TAG_SYSTEM, error_msg, context=True)
        else:
            message = f"The result of the action {model_response.action.name} is:\n"
            message += f"{result['message']}\n"
            self.msgs.add_visible(TAG_SYSTEM, message, context=False)
            full_result = f"Action executed: {json.dumps(result, indent=2)}"
            self.msgs.add_invisible(TAG_SYSTEM_INTERNAL,
                                    full_result,
                                    context=True)

            # Check if immediate response is needed for this action type
            params_dict = model_response.action.params.model_dump() if hasattr(
                model_response.action.params,
                'model_dump') else model_response.action.params

            if params_dict.get("immediate_response", False):
                self.msgs.set_control_flag("auto_continue", full_result)
                self.msgs.add_visible(TAG_SYSTEM,
                                      "Auto-continuing with action result",
                                      context=False)

    def handle_memory_approval(self, user_input):
        """Handle user approval for memory operations."""
        # Add user input first
        # self.msgs.add_visible(TAG_USER_INPUT, user_input, context=False)

        output = ""
        if user_input.lower() in ["y", "yes"]:
            try:
                key = self._pending_memory["key"]
                value = self._pending_memory["value"]
                self.memory_manager.write_to_memory(key, value)
                output += f"Memory saved with key: {key}\n"
                self.logger.info(
                    f"User approved and memory saved with key: {key}")
                self._pending_memory = None
            except Exception as e:
                self.logger.error(f"Error saving memory: {e}")
                output += f"Error saving memory: {e}\n"
            return output

        elif user_input.lower() in ["n", "no"]:
            self._pending_memory = None
            self.logger.info("Memory addition discarded by user.")
            output += "Memory addition discarded.\n"
            return output

        self.logger.warning(
            "Invalid response received during approval process.")
        return "Invalid response. Please reply with 'y' or 'n'.\n"

    def render(self):
        """Render the current animation sequence."""
        try:
            latest_sequence, latest_step = self.animation_manager.get_latest_sequence_with_step(
            )
            if not latest_sequence:
                self.logger.warning(
                    "No animation sequence available to render.")
                return "No animation sequence available to render."

            animation_json = json.loads(latest_sequence)
            self.animation_manager.render(animation_json)
            self.logger.info(
                f"Animation step {latest_step} rendered successfully.")
            return f"Animation step {latest_step} rendered successfully."
        except Exception as e:
            self.logger.error(f"Error rendering animation: {e}")
            return f"Error rendering animation: {e}"

    def stop(self):
        """Stop the current animation rendering."""
        try:
            if self.animation_manager.renderer:
                self.animation_manager.renderer.stop()
                return "Animation rendering stopped."
            else:
                return "No renderer available to stop."
        except Exception as e:
            self.logger.error(f"Error stopping animation rendering: {e}")
            return f"Error stopping animation: {e}"
