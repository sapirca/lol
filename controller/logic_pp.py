import random
from controller.backends import GPTBackend, ClaudeBackend, LLMBackend, GeminiBackend
from memory.memory_manager import MemoryManager
from prompts.main_prompt import intro_prompt
from music.song_provider import SongProvider
import xml.etree.ElementTree as ET
from controller.interpreter import Interpreter
from controller.formatter import Formatter
from constants import MESSAGE_SNAPSHOT_FILE, CONFIG_FILE
from controller.message_streamer import MessageStreamer
import logging
import os
from datetime import datetime
import json
# from config import config as basic_config
# from configs.config_conceptual import config as basic_config
from configs.config_kivsee import config as basic_config
from animation.animation_manager import AnimationManager
from controller.actions import (ActionRegistry, UpdateAnimationAction,
                                GetAnimationAction, GetMemoryAction,
                                GetMusicStructureAction, ResponseToUserAction)
from schemes.main_schema import MainSchema
from typing import Dict, Any


class LogicPlusPlus:

    def __init__(self, snapshot_dir=None):
        """Initialize the LogicPlusPlus, optionally loading from a snapshot."""
        self.logger = logging.getLogger("LogicPlusPlusLogger")
        self.wait_for_save_approval = False
        self.temp_animation_path = None
        self.message_streamer = MessageStreamer()
        self.song_provider = SongProvider()
        self.backends = {}

        # Initialize action registry
        self.action_registry = ActionRegistry()

        if snapshot_dir is not None:
            try:
                self._load_from_snapshot(snapshot_dir)
                self.initial_prompt_added = True
            except Exception as e:
                self.logger.error(
                    f"Failed to load snapshot from {snapshot_dir}: {e}")
                raise RuntimeError(
                    f"Failed to load snapshot from {snapshot_dir}: {e}")
        else:
            # Default initialization if no snapshot is provided
            self.initial_prompt_added = False
            self.config = basic_config
            self.selected_framework = self.config.get("framework", None)
            self.animation_manager = AnimationManager(self.selected_framework,
                                                      self.message_streamer)

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
        self.formatter = Formatter(self.message_streamer,
                                   self.animation_manager)

        self._register_actions()

    def _register_actions(self):
        """Register all available actions"""
        self.action_registry.register_action(
            "update_animation", UpdateAnimationAction(self.animation_manager))
        self.action_registry.register_action(
            "get_animation", GetAnimationAction(self.animation_manager))
        self.action_registry.register_action(
            "get_memory", GetMemoryAction(self.memory_manager))
        self.action_registry.register_action(
            "get_music_structure", GetMusicStructureAction(self.song_provider))
        self.action_registry.register_action("response_to_user",
                                             ResponseToUserAction())

    def shutdown(self, shutdown_snapshot_dir=None):
        if not shutdown_snapshot_dir:
            timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
            shutdown_snapshot_dir = os.path.join(
                self.message_streamer.snapshots_dir,
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
            json.dump(self.message_streamer.messages, file,
                      indent=4)  # Save only the messages data

        # Finalize the message_streamer
        self.message_streamer.finalize()

        return (f"Snapshot saved: {shutdown_snapshot_dir}.")

    def get_visible_chat(self):
        """Retrieve all visible chat messages from the message_streamer, including their tags/labels."""
        return [(message['timestamp'], message['content'], message['tag'])
                for message in self.message_streamer.messages
                if message['visible'] and 'timestamp' in message]

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
            self.message_streamer.load(messages_snapshot_file)
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
                                                  self.message_streamer)
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

    def build_prompt(self, intro_prompt, general_knowledge):
        prompt_parts = []
        if intro_prompt:
            prompt_parts.append(intro_prompt)
        if general_knowledge:
            prompt_parts.append("\n### General Knowledge\n")
            prompt_parts.append(general_knowledge)
        return "\n".join(prompt_parts)

    def process_init_prompt(self):
        latest_sequence = None
        if not self.initial_prompt_added:

            # # Provide song structure
            # song_name = self.config.get("song_name")
            # song_info = self.song_provider.get_song_structure(
            #     song_name) if song_name else ""
            # print(f" >>> Song name: {song_name}")

            # Provide general knowledge
            timing_knowledge = self.animation_manager.get_general_knowledge()

            # Build the initial prompt
            initial_prompt = self.build_prompt(intro_prompt, timing_knowledge)

            self.message_streamer.add_message("initial_prompt_context",
                                              initial_prompt,
                                              visible=False,
                                              context=True)

            # # Add memory to the initial prompt
            # memory = self.memory_manager.get_memory()
            # if memory:
            #     self.message_streamer.add_message("system",
            #                                       f"Memory: {memory}",
            #                                       visible=False,
            #                                       context=True)

            # Do not add the last animation
            # latest_sequence = self.animation_manager.get_latest_sequence()
            # if (latest_sequence):
            #     self.message_streamer.add_message("initial_animation",
            #                                       latest_sequence,
            #                                       visible=False,
            #                                       context=True)

            self.initial_prompt_added = True

            initial_prompt_report = (
                f"Included initial prompt. Sent to {self.selected_backend}. {self.selected_framework} framework.\n"
            )

            self.message_streamer.add_message("system",
                                              initial_prompt_report,
                                              visible=True,
                                              context=False)

            return initial_prompt_report

    def communicate(self, user_input):
        system_responses = []
        if self.wait_for_save_approval:
            # Handle confirmation for pending action
            self.message_streamer.add_message("user_input",
                                              user_input,
                                              visible=True,
                                              context=False)
            result = self.handle_user_approval(user_input)

            self.message_streamer.add_message("system_output",
                                              result,
                                              visible=True,
                                              context=False)
            system_responses.append(("system", result))
            return system_responses

        backend = self.select_backend()
        initial_prompt_report = self.process_init_prompt()
        if (initial_prompt_report):
            system_responses.append(("system", initial_prompt_report))

        self.message_streamer.add_message("user_input",
                                          user_input,
                                          visible=True,
                                          context=True)

        messages = self.formatter.build_messages()
        auto_continue = False
        try:
            model_response = backend.generate_response(messages)
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.message_streamer.add_message("system",
                                              error_msg,
                                              visible=True,
                                              context=False)
            system_responses.append(("system", error_msg))
            return system_responses

        # Display the LLM's reasoning about the chosen action and overall strategy
        self.message_streamer.add_message("assistant",
                                          "Reasoning:\n" +
                                          model_response.reasoning,
                                          visible=True,
                                          context=True)
        system_responses.append(("assistant", model_response.reasoning))

        # Show the action plan if provided
        if model_response.actions_plan:
            message = f"Actions plan:\n"
            message += f"{model_response.actions_plan}\n"
            self.message_streamer.add_message("assistant",
                                              message,
                                              visible=True,
                                              context=True)
            system_responses.append(("assistant", message))

        if not model_response.action:
            message = f"No action to execute.\n"
            self.message_streamer.add_message("system",
                                              message,
                                              visible=True,
                                              context=True)
            system_responses.append(("system", message))
            return system_responses

        message = f"I will execute the action {model_response.action.name} with the following parameters:\n"
        message += f"{model_response.action.params}\n"

        self.message_streamer.add_message("assistant",
                                          message,
                                          visible=True,
                                          context=True)
        system_responses.append(("assistant", message))

        # Execute single action for this turn and handle its result
        result = self.action_registry.execute_action(
            model_response.action.name, model_response.action.params)

        if result["status"] == "error":
            error_msg = f"Error executing action {model_response.action.name}: {result['message']}"
            self.message_streamer.add_message("system",
                                              error_msg,
                                              visible=True,
                                              context=False)
            system_responses.append(("system", error_msg))
            # Add error result to context
            action_result = {
                "action": model_response.action.name,
                "status": "error",
                "error": result["message"]
            }
        else:
            # Handle successful action execution and prepare response
            self.wait_for_save_approval = result.get("requires_confirmation",
                                                     False)

            if model_response.action.name == "update_animation" and "temp_path" in result:
                self.temp_animation_path = result["temp_path"]

            message = f"The result of the action {model_response.action.name} is:\n"
            message += f"{result['message']}\n"
            self.message_streamer.add_message("assistant",
                                              message,
                                              visible=True,
                                              context=True)
            system_responses.append(("assistant", message))

            action_result = {
                "action": model_response.action.name,
                "status": "success",
                "message": result["message"]
            }
            if "data" in result:
                action_result["data"] = result["data"]
                data_msg = f"Action data {model_response.action.name}, returned value: {json.dumps(result['data'], indent=2)}"
                self.message_streamer.add_message("assistant",
                                                  data_msg,
                                                  visible=True,
                                                  context=True)
                system_responses.append(("assistant", data_msg))

            # Check if immediate response is needed for this action type
            params_dict = model_response.action.params.model_dump() if hasattr(
                model_response.action.params,
                'model_dump') else model_response.action.params

            if params_dict.get("immediate_response", False):
                auto_continue = True
                self.message_streamer.add_message(
                    "system",
                    "Auto-continuing with action result",
                    visible=True,
                    context=True)
                system_responses.append(
                    ("system", "Auto-continuing with action result"))

        # Store action result in context for next LLM turn
        results_str = json.dumps(action_result, indent=2)
        self.message_streamer.add_message("action_results",
                                          f"Action Result:\n{results_str}",
                                          visible=True,
                                          context=True)

        if auto_continue:
            system_responses.append(("auto_continue", results_str))

        return system_responses

    # def act_on_response(self, model_response, printable_response):
    #     output = ""

    #     try:
    #         if model_response:
    #             # Use `exclude_none=True` to remove null fields from the animation JSON
    #             animation_str = json.dumps(
    #                 model_response,
    #                 indent=4,
    #                 default=lambda o: o.model_dump(exclude_none=True))

    #             # Save the animation sequence to a temporary file
    #             self.temp_animation_path = self.animation_manager.save_tmp_animation(
    #                 animation_str)
    #             self.logger.info(
    #                 f"Generated {self.temp_animation_path} for the user's observation."
    #             )

    #             output += f"Animation sequence generated and saved to:\n"
    #             output += f"{self.temp_animation_path}\n"
    #             output += "Do you want me to save a snapshot to the sequence manager? (y/n)\n"
    #             self.wait_for_save_approval = True

    #             # Auto-render the animation for preview if auto_render is enabled in the config
    #             if self.config.get("auto_render", False):
    #                 animation_dict = json.loads(animation_str)
    #                 render_result = self.render_preview(animation_dict)
    #                 if "Error" in render_result:
    #                     output += f"{render_result}\nAnimation was not rendered for preview.\n"
    #                 else:
    #                     output += f"{render_result}\n"

    #     except Exception as e:
    #         self.logger.error(
    #             f"Error processing response and rendering animation: {e}")
    #         output += f"Error processing response and rendering animation: {e}\n"

    #     return output

    def handle_user_approval(self, user_input):
        output = ""
        if user_input.lower() in ["y", "yes"]:
            if self.temp_animation_path:  # Ensure there's an animation path to process
                step_number = len(
                    self.animation_manager.sequence_manager.steps) + 1
                try:
                    with open(self.temp_animation_path, "r") as temp_file:
                        animation_sequence = temp_file.read()

                    # Save the animation sequence to the message streamer
                    # This is distinct from the 'preview' message if the user approves saving
                    self.message_streamer.add_message("animation_update",
                                                      animation_sequence,
                                                      visible=False,
                                                      context=False)

                    # Add the animation to the sequence manager
                    seq_message = self.animation_manager.add_sequence(
                        step_number, animation_sequence)

                    self.message_streamer.add_message("animation_update",
                                                      seq_message,
                                                      visible=False,
                                                      context=False)

                    output += f"Animation sequence added to the sequence manager as step {step_number}.\n"
                    self.logger.info(
                        "User approved and animation saved to sequence manager."
                    )

                except Exception as e:
                    self.logger.error(
                        f"Error saving animation from temp file to sequence manager: {e}"
                    )
                    output += f"Error saving animation: {e}\n"
            else:
                output += "No pending animation to save. Should not happen. Please report this bug.\n"
                self.logger.warning(
                    "User approved, but no temporary animation path was set.")

            self.temp_animation_path = None
            self.wait_for_save_approval = False
            self.logger.info("User approval received.")
            return output

        elif user_input.lower() in ["n", "no"]:
            if self.temp_animation_path:
                self.animation_manager.delete_temp_file(
                    self.temp_animation_path)
                self.temp_animation_path = None
                self.logger.info("Animation discarded by user.")
                output += "Animation discarded.\n"
            else:
                output += "Action discarded (no pending animation to discard).\n"
                self.logger.warning(
                    "User discarded, but no temporary animation path was set.")

            self.wait_for_save_approval = False
            return output

        self.logger.warning(
            "Invalid response received during approval process.")
        return "Invalid response. Please reply with 'y' or 'n'.\n"

    def delete_temp_file(self, file_path):
        absolute_path = os.path.abspath(file_path)
        try:
            if os.path.exists(absolute_path):
                os.remove(absolute_path)
                if not os.path.exists(absolute_path):
                    self.logger.info(
                        f"Temp file {absolute_path} was successfully deleted.")
                else:
                    self.logger.error(
                        f"Error: Temp file {absolute_path} still exists after deletion attempt."
                    )
            else:
                self.logger.warning(
                    f"Temp file {absolute_path} does not exist.")
        except Exception as e:
            self.logger.error(
                f"An error occurred while deleting {absolute_path}: {e}")

    def render(self):
        """Render the current animation sequence."""
        try:
            latest_sequence = self.animation_manager.get_latest_sequence()
            if not latest_sequence:
                self.logger.warning(
                    "No animation sequence available to render.")
                return "No animation sequence available to render."

            # Get the current step number
            current_step = len(self.animation_manager.sequence_manager.steps)

            animation_json = json.loads(latest_sequence)
            self.animation_manager.render(animation_json)
            self.logger.info(
                f"Animation step {current_step} rendered successfully.")
            return f"Animation step {current_step} rendered successfully."
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
            return f"Error stopping animation rendering: {e}"
