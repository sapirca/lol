import random
from controller.backends import GPTBackend, ClaudeBackend, GeminiBackend, StubBackend, LLMBackend, DeepSeekBackend
from prompt import intro_prompt
from animation.songs.song_provider import SongProvider
import xml.etree.ElementTree as ET
from interpreter import Interpreter
from formatter import Formatter
from controller.constants import MESSAGE_SNAPSHOT_FILE, CONFIG_FILE
from controller.message_streamer import MessageStreamer
import logging
import os
from datetime import datetime
import json
from config import config as basic_config
from animation.animation_manager import AnimationManager


class LogicPlusPlus:

    def __init__(self, snapshot_dir=None):
        """Initialize the LogicPlusPlus, optionally loading from a snapshot."""
        self.logger = logging.getLogger("LogicPlusPlusLogger")
        self.wait_for_response = False
        self.temp_animation_path = None
        self.message_streamer = MessageStreamer()
        self.song_provider = SongProvider()
        self.backends = {}
        self._initialize_backends()

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

        # Shared initialization logic
        self.selected_backend = self.config.get("selected_backend", None)
        self.response_manager = Interpreter(self.animation_manager)
        self.formatter = Formatter(self.message_streamer,
                                   self.animation_manager)

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
            "DeepSeek": DeepSeekBackend,
            "Stub": StubBackend
        }
        for backend_name, backend_class in backend_mapping.items():
            self.register_backend(backend_class(name=backend_name))

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

    def build_prompt(self, intro_prompt, general_knowledge,
                     animation_knowledge, song_structure, world_structure):
        prompt_parts = []
        if intro_prompt:
            prompt_parts.append(intro_prompt)
        if general_knowledge:
            prompt_parts.append("\n### General Knowledge\n")
            prompt_parts.append(general_knowledge)
        if animation_knowledge:
            prompt_parts.append("\n### Animation Knowledge\n")
            prompt_parts.append(animation_knowledge)
        if song_structure:
            prompt_parts.append("\n### Song Structure\n")
            prompt_parts.append(song_structure)
        if world_structure:
            prompt_parts.append("\n### World Structure\n")
            prompt_parts.append(world_structure)
        return "\n".join(prompt_parts)

    def communicate(self, user_input):
        system_responses = []
        if self.wait_for_response:
            # User response for agent action (e.g., store to memory, update animation)
            # This does not need to be added to the LLM context.
            self.message_streamer.add_message(
                "user_input", user_input, visible=True, context=False
            )  # Need to add info that this is internal_actions communication
            visible_system_message = self.handle_user_approval(user_input)
            self.message_streamer.add_message(
                "system_output",
                visible_system_message,
                visible=True,
                context=False
            )  # Need to add info that this is internal_actions communication
            system_responses.append(("system", visible_system_message))
            return system_responses

        backend = self.select_backend()

        latest_sequence = None
        if not self.initial_prompt_added:
            song_name = self.config.get("song_name", None)
            if (song_name is None) or (song_name
                                       not in self.song_provider.song_names):
                raise ValueError(
                    f"Invalid song name '{song_name}'. Available songs: {self.song_provider.song_names}"
                )
            print(f" >>> Song name: {song_name}")

            world_structure = self.animation_manager.get_world_structure()
            general_knowledge = self.animation_manager.get_general_knowledge()
            animation_knowledge = self.animation_manager.get_domain_knowledge()
            song_structure = self.song_provider.get_song_structure(song_name)

            # Get the song from the song provider
            initial_prompt = self.build_prompt(intro_prompt,
                                               animation_knowledge,
                                               general_knowledge,
                                               song_structure, world_structure)

            # Ensure the main instructions are always sent to the LLM for proper context.
            self.message_streamer.add_message("initial_prompt_context",
                                              initial_prompt,
                                              visible=False,
                                              context=True)

            # Always send the original animation structure to the LLM for reference.
            latest_sequence = self.animation_manager.get_latest_sequence()
            self.message_streamer.add_message("initial_animation",
                                              latest_sequence,
                                              visible=False,
                                              context=True)
            self.initial_prompt_added = True

            initial_prompt_report = (
                f"Request sent to {self.selected_backend} with the following information"
                f"\n  * General prompt and knowledge files"
                f"\n  * {self.selected_framework}'s World structure file"
                f"\n  * {self.selected_framework}'s Animation sequence file"
                f"\n  * Song name: {song_name}")

            self.message_streamer.add_message("system",
                                              initial_prompt_report,
                                              visible=True,
                                              context=False)

            system_responses.append(("system", initial_prompt_report))

        self.message_streamer.add_message("user_input",
                                          user_input,
                                          visible=True,
                                          context=True)

        # Update the UI with the prompt that was sent

        # Build the messages array for the LLM
        messages = self.formatter.build_messages()
        response = backend.generate_response(messages)

        # The raw response contains a WIP animation which does not need to be added to the context.
        self.message_streamer.add_message("llm_raw_response",
                                          response,
                                          visible=False,
                                          context=False)

        parsed_response = self.response_manager.parse_response(response)

        assistant_response = parsed_response.get("response_wo_animation",
                                                 "") or ""
        # Add this trimmed short response to the context
        # for better understanding.
        self.message_streamer.add_message("assistant",
                                          assistant_response +
                                          " The animation was trimmed out",
                                          visible=True,
                                          context=True)

        act_on_response_msg = self.act_on_response(parsed_response)
        self.message_streamer.add_message(
            "system_output", act_on_response_msg, visible=True,
            context=False)  # Information about agent actions shared
        # with the user.

        system_responses.append(("assistant", assistant_response))
        if act_on_response_msg:
            system_responses.append(("system", act_on_response_msg))
        return system_responses

    def act_on_response(self, processed_response):
        reasoning = processed_response.get("reasoning")
        consistency_justification = processed_response.get(
            "consistency_justification")
        animation_sequence = processed_response.get("animation_sequence")

        output = ""

        if animation_sequence:
            self.temp_animation_path = self.animation_manager.store_temp_animation(
                animation_sequence)
            self.logger.info(
                f"Generated {self.temp_animation_path} for the user's observation."
            )
            self.wait_for_response = True

            output += f"Animation sequence generated and saved to {self.temp_animation_path}\n"
            output += "Preview and edit the animation as needed.\n"
            output += "Save this temporary animation file to the sequence manager? (y/n): "

        for action in processed_response.get("requested_actions", []):
            output += f"Unhandled action: {action['action']}\n"

        return output

    def handle_user_approval(self, user_input):
        if user_input.lower() in ["y", "yes"]:
            step_number = len(
                self.animation_manager.sequence_manager.steps) + 1
            with open(self.temp_animation_path, "r") as temp_file:
                animation_sequence = temp_file.read()
            self.message_streamer.add_message(
                "animation_update",
                animation_sequence,
                visible=False,
                context=False)  # save every sequence update to streamer
            seq_message = self.animation_manager.add_sequence(
                step_number, animation_sequence)
            self.message_streamer.add_message("animation_update",
                                              seq_message,
                                              visible=False,
                                              context=False)
            self.animation_manager.delete_temp_file(self.temp_animation_path)
            self.wait_for_response = False
            self.logger.info("Animation approved and saved.")
            return f"Animation saved successfully as step {step_number}.\n"

        elif user_input.lower() in ["n", "no"]:
            self.animation_manager.delete_temp_file(self.temp_animation_path)
            self.wait_for_response = False
            self.logger.info("Animation discarded by user.")
            return "Animation discarded.\n"

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
