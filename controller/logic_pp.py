import random
from controller.backends import GPTBackend, ClaudeBackend, LLMBackend, GeminiBackend
from memory.memory_manager import MemoryManager
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
from animation.compound_effects_manager import CompoundEffectsManager
from controller.actions import (
    ActionRegistry, UpdateAnimationAction, GetAnimationAction,
    AddToMemoryAction, QuestionAction, MemorySuggestionAction,
    AnswerUserAction, GenerateBeatBasedEffectAction, RemoveMemoryAction,
    UpdateMemoryAction, GetMusicStructureAction, SaveCompoundEffectAction,
    GetCompoundEffectAction, GetCompoundEffectsKeysAndTagsAction,
    GetRandomEffectAction, DeleteRandomEffectAction)
from schemes.main_schema import MainSchema
from typing import Dict, Any
import threading
from schemes.system_schema import SummarizationResponse


def load_and_merge_configs(snapshot_config_path=None):
    """Load and merge main config with snapshot config if provided."""
    # Load main config
    main_config_path = os.path.join("configs", "main_config.json")
    try:
        with open(main_config_path, "r") as f:
            main_config = json.load(f)
    except Exception as e:
        logging.error(f"Error loading main config: {e}")
        raise RuntimeError(f"Error loading main config: {e}")

    # If no snapshot config provided, return main config
    if snapshot_config_path is None:
        snapshot_config = basic_config
    else:
        try:
            with open(snapshot_config_path, "r") as f:
                snapshot_config = json.load(f)
        except Exception as e:
            logging.error(f"Error loading snapshot config: {e}")
            raise RuntimeError(f"Error loading snapshot config: {e}")

    # Check for duplicate keys
    duplicate_keys = set(main_config.keys()) & set(snapshot_config.keys())
    if duplicate_keys:
        raise RuntimeError(
            f"Duplicate keys found in configs: {duplicate_keys}. Snapshot config path: {snapshot_config_path}"
        )

    # Merge configs (snapshot config takes precedence)
    merged_config = {**main_config, **snapshot_config}
    return merged_config


class LogicPlusPlus:

    def __init__(self, snapshot_dir=None, restart_config=None):
        """Initialize the LogicPlusPlus, optionally loading from a snapshot or restarting with latest sequence."""
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

        if restart_config is not None:
            # Handle restart with latest sequence
            self._restart_with_latest_sequence(restart_config)
        elif snapshot_dir is not None:
            try:
                self._load_from_snapshot(snapshot_dir)
            except Exception as e:
                self.logger.error(
                    f"Failed to load snapshot from {snapshot_dir}: {e}")
                raise RuntimeError(
                    f"Failed to load snapshot from {snapshot_dir}: {e}")
        else:
            # Default initialization if no snapshot is provided
            self.config = load_and_merge_configs()
            self.selected_framework = self.config.get("framework", None)
            self.animation_manager = AnimationManager(self.selected_framework,
                                                      self.msgs)

        # Initialize compound effects manager
        self.compound_effects_manager = CompoundEffectsManager()

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

        self._register_actions()

        self.formatter = Formatter(self.msgs, self.animation_manager,
                                   self.memory_manager, self.song_provider,
                                   self.action_registry, self.config)

    def _register_actions(self):
        """Register all available actions"""
        self.action_registry.register_action(
            "update_animation",
            UpdateAnimationAction(
                self.animation_manager,
                self.msgs,
                config=self.config,
            ))
        self.action_registry.register_action(
            "get_animation",
            GetAnimationAction(self.animation_manager, self.msgs))
        self.action_registry.register_action(
            "add_to_memory", AddToMemoryAction(self.memory_manager, self.msgs))
        self.action_registry.register_action("question",
                                             QuestionAction(self.msgs))
        self.action_registry.register_action("memory_suggestion",
                                             MemorySuggestionAction(self.msgs))
        self.action_registry.register_action("answer_user",
                                             AnswerUserAction(self.msgs))
        self.action_registry.register_action(
            "generate_beat_based_effect",
            GenerateBeatBasedEffectAction(self.msgs))
        self.action_registry.register_action(
            "remove_memory", RemoveMemoryAction(self.memory_manager,
                                                self.msgs))
        self.action_registry.register_action(
            "update_memory", UpdateMemoryAction(self.memory_manager,
                                                self.msgs))
        self.action_registry.register_action(
            "get_music_structure",
            GetMusicStructureAction(self.song_provider, self.msgs))

        # Register compound effects actions
        self.action_registry.register_action(
            "save_compound_effect",
            SaveCompoundEffectAction(self.compound_effects_manager, self.msgs))
        self.action_registry.register_action(
            "get_compound_effect",
            GetCompoundEffectAction(self.compound_effects_manager, self.msgs))
        self.action_registry.register_action(
            "get_compound_effects_keys_and_tags",
            GetCompoundEffectsKeysAndTagsAction(self.compound_effects_manager,
                                                self.msgs))

        # Register random effect actions
        self.action_registry.register_action(
            "get_random_effect",
            GetRandomEffectAction(self.compound_effects_manager, self.msgs))
        self.action_registry.register_action(
            "delete_random_effect",
            DeleteRandomEffectAction(self.compound_effects_manager, self.msgs))

    def shutdown(self, requested_shutdown_snapshot_dir=None):
        if not requested_shutdown_snapshot_dir:
            timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
            shutdown_snapshot_dir = os.path.join(
                self.msgs.snapshots_dir,
                f"{timestamp}_{self.selected_framework}_{self.selected_backend}"
            )
            os.makedirs(shutdown_snapshot_dir, exist_ok=True)
        else:
            shutdown_snapshot_dir = os.path.join(
                self.msgs.snapshots_dir, requested_shutdown_snapshot_dir)
            if not os.path.exists(shutdown_snapshot_dir):
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
                content_trimmed = message['content'][:60] + "..."
                chat_history.append(
                    (message['timestamp'],
                     f"{message['tag']} {content_trimmed}", message['tag'],
                     message['visible'], message['context']))
        return chat_history

    def _load_from_snapshot(self, snapshot_dir):
        """Load configuration and messages from a snapshot directory."""
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

        # Load and merge configurations
        snapshot_config_file = os.path.join(snapshot_dir, CONFIG_FILE)
        self.config = load_and_merge_configs(snapshot_config_file)

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

    def _add_action_result_to_messages(self, result, prefix="Action"):
        """Helper method to add action results to messages."""
        if result:
            # Add the action result message
            self.msgs.add_visible(TAG_ACTION_RESULTS,
                                  f"{prefix}: {result.get('message', '')}",
                                  context=True)
            # Add the data if present
            if "data" in result:
                self.msgs.add_invisible(TAG_ACTION_RESULTS,
                                        json.dumps(result["data"], indent=2),
                                        context=True)
        return result

    def execute_pending_action(self):
        """Execute the pending action in the action registry."""
        result = self.action_registry.execute_pending_action()
        return self._add_action_result_to_messages(result, "Action executed")

    def cancel_pending_action(self):
        """Cancel the pending action in the action registry."""
        result = self.action_registry.cancel_pending_action()
        return self._add_action_result_to_messages(result, "Action cancelled")

    def _communicate_internal(self, user_input):
        """Internal communication method that contains the original communicate logic."""
        # Check if we're auto-continuing with an action result
        control_flags = self.msgs.get_and_clear_control_flags()
        if control_flags.get("auto_continue"):
            # Get the last action result and add it to messages
            last_result = self.action_registry.get_last_action_result()
            if last_result and "data" in last_result:
                self.msgs.add_invisible(
                    TAG_ACTION_RESULTS,
                    "Here's the action result:\n " +
                    json.dumps(last_result["data"], indent=2),
                    context=True)
                self.msgs.add_invisible(
                    TAG_ACTION_RESULTS,
                    "Please process the action result and continue.",
                    context=True)
                self.msgs.add_visible(TAG_SYSTEM,
                                      "Processing action result...",
                                      context=False)

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
        action_tag = f"[Action: \"{model_response.action.name}\"]: "
        response_message += action_tag + model_response.reasoning

        # Execute single action for this turn and handle its result
        result = self.action_registry.execute_action(
            model_response.action.name, model_response.action.params)

        if result["status"] == "error":
            self.msgs.add_visible(TAG_ASSISTANT,
                                  response_message,
                                  context=True)
            error_msg = f"Error executing action {model_response.action.name}: {result['message']}"
            self.msgs.add_visible(TAG_SYSTEM, error_msg, context=False)
            self.msgs.add_visible(TAG_SYSTEM_INTERNAL,
                                  error_msg + "\n Consider trying again.",
                                  context=True)
        else:
            response_message += "\n\n" + result.get("message",
                                                    "No message? Debug!")
            self.msgs.add_visible(TAG_ASSISTANT,
                                  response_message,
                                  context=True)

            # If there's data in the result, send it back to LLM for processing
            if "data" in result:
                self.msgs.add_invisible(TAG_ACTION_RESULTS,
                                        json.dumps(result["data"], indent=2),
                                        context=True)
                # # Set auto-continue flag to process the result
                # self.msgs.set_control_flag("auto_continue", True)

    def render(self, store_animation=False):
        """Render the current animation sequence."""
        try:
            result = self.animation_manager.get_latest_sequence_with_step()
            if not result:
                self.logger.warning(
                    "No animation sequence available to render.")
                return "No animation sequence available to render."

            latest_sequence, latest_step = result
            animation_json = json.loads(latest_sequence)
            self.animation_manager.render(animation_json,
                                          song_name="aladdin",
                                          store_animation=store_animation)
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

    def _restart_with_latest_sequence(self, old_controller):
        """Restart with the latest sequence from the old controller."""
        # Copy config from old controller
        self.config = old_controller.config.copy()
        self.selected_framework = self.config.get("framework", None)

        # Initialize new animation manager
        self.animation_manager = AnimationManager(self.selected_framework,
                                                  self.msgs)

        # Get latest sequence from old controller
        latest_sequence = old_controller.animation_manager.get_latest_sequence(
        )
        if latest_sequence:
            # Add the latest sequence to the new controller
            self.animation_manager.add_sequence(latest_sequence)

    def reduce_tokens(self):
        """Summarize the conversation and create a new message streamer with the summary."""
        try:
            # Build the summarization prompt using the formatter
            messages = self.formatter.build_summarization_messages()

            # Get the backend and generate summary
            backend = self.select_backend()
            try:
                model_response = backend.generate_response(
                    messages, SummarizationResponse)
                summary = f"{model_response.summary}\n\nAnimation Summary:\n{model_response.animation_summary}"
                if model_response.pending_tasks:
                    summary += "\n\nPending Tasks:\n" + "\n".join(
                        f"- {task}" for task in model_response.pending_tasks)

                # Create a new message streamer only after getting the summary
                new_msgs = MessageStreamer()

                # Add the summary to the new message streamer
                new_msgs.add_visible(TAG_SYSTEM,
                                     "Conversation Summary:",
                                     context=True)
                new_msgs.add_visible(TAG_ASSISTANT, summary, context=True)

                # Replace the old message streamer with the new one
                self.msgs = new_msgs

                return "Successfully reduced tokens by summarizing the conversation."
            except Exception as e:
                self.logger.error(f"Error generating summary: {e}")
                return f"Error generating summary: {str(e)}"

        except Exception as e:
            self.logger.error(f"Error reducing tokens: {e}")
            return f"Error reducing tokens: {str(e)}"

    def get_pending_action_info(self):
        """Get information about the pending action from the action registry."""
        return self.action_registry.get_pending_action_info()

    def get_last_action_result(self):
        """Get the last action result from the action registry."""
        return self.action_registry.get_last_action_result()
