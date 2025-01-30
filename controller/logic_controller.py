import random
from controller.backends import GPTBackend, ClaudeBackend, GeminiBackend, StubBackend, LLMBackend
from prompts import get_full_prompt
import xml.etree.ElementTree as ET
from interpreter import Interpreter
from formatter import Formatter
from controller.constants import ANIMATION_OUT_TEMP_DIR, XLIGHTS_HOUSE_PATH, XLIGHTS_SEQUENCE_PATH
from animation.sequence_manager import SequenceManager
from logger import Logger
import os
from datetime import datetime
import json
from config import config as basic_config
from controller.constants import TIME_FORMAT

class LogicPlusPlus:

    def __init__(self, snapshot_dir=None):
        """Initialize the LogicPlusPlus, optionally loading from a snapshot."""
        self.logger = Logger()
        self.backends = {}
        self.house_config = self._load_house_config()
        self.wait_for_response = False
        self.temp_animation_path = None
        self._initialize_backends()
        self.sequence_manager = SequenceManager(XLIGHTS_SEQUENCE_PATH,
                                                self.logger)
        self.formatter = Formatter(self.logger, self.sequence_manager)

        if snapshot_dir is not None:
            try:
                self._load_from_snapshot(snapshot_dir)
                self.initial_prompt_added = True
            except Exception as e:
                raise RuntimeError(
                    f"Failed to load snapshot from {snapshot_dir}: {e}")
        else:
            # Default initialization if no snapshot is provided
            self.initial_prompt_added = False
            self.config = basic_config

        # Shared initialization logic
        self.use_stub = self.config.get("use_stub", False)
        self.selected_backend = self.config.get("selected_backend", None)
        self.response_manager = Interpreter(self.sequence_manager)

    def shutdown(self):
        timestamp = datetime.now().strftime("%YY%m%d_%H%M%S")
        snapshot_dir = os.path.join(self.logger.log_dir,
                                    f"snapshot_{timestamp}")
        os.makedirs(snapshot_dir, exist_ok=True)

        # Save configuration
        snapshot_config_file = os.path.join(snapshot_dir, "config.json")
        with open(snapshot_config_file, "w") as file:
            json.dump(self.config, file, indent=4)

        # Save all animations
        all_animations = self.sequence_manager.get_all_sequences()
        animations_dir = os.path.join(snapshot_dir, "animations")
        os.makedirs(animations_dir, exist_ok=True)
        for i, animation in enumerate(all_animations, start=1):
            animation_file = os.path.join(animations_dir, f"animation_{i}.xml")
            with open(animation_file, "w") as file:
                file.write(animation)

        # Save logs to logs.json
        logs_json_file = os.path.join(snapshot_dir, "logs.json")
        with open(logs_json_file, "w") as file:
            json.dump(self.logger.logs, file,
                      indent=4)  # Save only the logs data

        # Finalize the logger
        self.logger.finalize()

        print(f"Session finalized. Snapshot saved in {snapshot_dir}.")

    def get_visible_chat(self):
        """Retrieve all visible chat messages from the logger, including their tags/labels."""
        return [(log['timestamp'], log['content'], log['tag'])
                for log in self.logger.logs
                if log['visible'] and 'timestamp' in log]

    def _load_from_snapshot(self, snapshot_dir):
        if not os.path.exists(snapshot_dir):
            raise FileNotFoundError(
                f"Snapshot directory '{snapshot_dir}' does not exist.")

        # Check required files
        required_files = ["logs.json", "config.json"]
        for file_name in required_files:
            if not os.path.exists(os.path.join(snapshot_dir, file_name)):
                error_msg = f"Required file '{file_name}' is missing in the snapshot directory."
                raise FileNotFoundError(error_msg)

        animations_dir = os.path.join(snapshot_dir, "animations")
        if not os.path.exists(animations_dir):
            raise FileNotFoundError(
                "Animations directory is missing in the snapshot directory.")

        # Load logs
        snapshot_log_file = os.path.join(snapshot_dir, "logs.json")
        try:
            self.logger.load(snapshot_log_file)
        except Exception as e:
            raise ValueError(f"Error loading logs: {e}")

        # Load configuration
        snapshot_config_file = os.path.join(snapshot_dir, "config.json")
        try:
            with open(snapshot_config_file, "r") as file:
                self.config = json.load(file)
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")

        # Load animations
        try:
            animations = []
            for animation_file in sorted(os.listdir(animations_dir)):
                animation_path = os.path.join(animations_dir, animation_file)
                with open(animation_path, "r") as file:
                    animations.append(file.read())
            self.sequence_manager.load_sequences(animations)
        except Exception as e:
            raise ValueError(f"Error loading animations: {e}")

        self.logger.add_log(
            f"Snapshot loaded successfully from {snapshot_dir}.")

    def _initialize_backends(self):
        backend_mapping = {
            "GPT": GPTBackend,
            "Claude": ClaudeBackend,
            "Gemini": GeminiBackend,
            "Stub": StubBackend
        }
        for backend_name, backend_class in backend_mapping.items():
            self.register_backend(backend_class(self.logger))

    def register_backend(self, backend):
        if not isinstance(backend, LLMBackend):
            raise TypeError("backend must be an instance of LLMBackend.")
        self.backends[backend.name] = backend

    def select_backend(self):
        if not self.backends:
            raise ValueError("No backends available.")

        if self.use_stub:
            stub_backend = self.backends.get("Stub")
            if not stub_backend:
                raise ValueError("Stub backend is not registered.")
            return stub_backend

        if self.selected_backend:
            selected_backend = self.backends.get(self.selected_backend)
            if selected_backend:
                return selected_backend

            print(
                f"Warning: Selected backend '{self.selected_backend}' not found, choosing randomly."
            )

        return random.choice(list(self.backends.values()))

    def _load_house_config(self):
        try:
            tree = ET.parse(XLIGHTS_HOUSE_PATH)
            root = tree.getroot()
            return ET.tostring(root, encoding='unicode')
        except Exception as e:
            return f"Error loading house configuration: {e}"

    def communicate(self, user_input):
        if self.wait_for_response:
            # User response for agent action (e.g., store to memory, update animation)
            # This does not need to be added to the LLM context.
            self.logger.add_message(
                "user_input", user_input, visible=True, context=False
            )  # Need to add info that this is internal_actions communication
            visible_system_message = self.handle_user_approval(user_input)
            self.logger.add_message(
                "system_output",
                visible_system_message,
                visible=True,
                context=False
            )  # Need to add info that this is internal_actions communication
            return {"system": visible_system_message}

        backend = self.select_backend()

        latest_sequence = None
        if not self.initial_prompt_added:
            initial_prompt = get_full_prompt(self.house_config)
            # Ensure the main instructions are always sent to the LLM for proper context.
            self.logger.add_message("initial_prompt_context",
                                    initial_prompt,
                                    visible=False,
                                    context=True)
            # Always send the original animation structure to the LLM for reference.
            latest_sequence = self.sequence_manager.get_latest_sequence()
            self.logger.add_message("initial_animation",
                                    latest_sequence,
                                    visible=False,
                                    context=True)
            self.initial_prompt_added = True

        self.logger.add_message("user_input",
                                user_input,
                                visible=True,
                                context=True)

        # Build the messages array for the LLM
        messages = self.formatter.build_messages()

        response = backend.generate_response(messages)

        # The raw response contains a WIP animation which does not need to be added to the context.
        self.logger.add_message("llm_raw_response",
                                response,
                                visible=False,
                                context=False)

        parsed_response = self.response_manager.parse_response(response)

        assistant_response = parsed_response.get("response_wo_animation",
                                                 "") or ""
        # Add this trimmed short response to the context
        # for better understanding.
        self.logger.add_message("assistant",
                                assistant_response +
                                " The animation was trimmed out",
                                visible=True,
                                context=True)

        system_response = self.act_on_response(parsed_response)
        self.logger.add_message(
            "system_output", system_response, visible=True,
            context=False)  # Information about agent actions shared
        # with the user.

        return {"assistant": assistant_response, "system": system_response}

    def act_on_response(self, processed_response):
        reasoning = processed_response.get("reasoning")
        consistency_justification = processed_response.get(
            "consistency_justification")
        animation_sequence = processed_response.get("animation_sequence")

        output = ""

        if animation_sequence:
            # Write the animation to a temp file
            output_dir = ANIMATION_OUT_TEMP_DIR
            os.makedirs(output_dir, exist_ok=True)

            temp_file_path = os.path.join(output_dir, "temp_animation.xml")
            self.temp_animation_path = os.path.abspath(temp_file_path)

            with open(self.temp_animation_path, "w") as temp_file:
                temp_file.write(animation_sequence)

            self.logger.add_log(
                "Generated temp_animation.xml for the user's observation.")
            self.wait_for_response = True

            output += f"An animation sequence was generated and saved in {self.temp_animation_path}\n"
            output += "Simulate or edit the file using xLights. Edit the animation file if needed.\n"
            output += "Approve to save this animation to the sequence manager once done. Approve? (y/n): "

        else:
            output += "No animation sequence provided in the LLM response.\n"

        for action in processed_response.get("requested_actions", []):
            output += f"Unhandled action: {action['action']}\n"

        return output

    def handle_user_approval(self, user_input):
        if user_input.lower() in ["y", "yes"]:
            step_number = len(self.sequence_manager.steps) + 1
            with open(self.temp_animation_path, "r") as temp_file:
                animation_sequence = temp_file.read()
            self.logger.add_message("animation_update",
                                    animation_sequence,
                                    visible=False,
                                    context=False)  # log every sequence update
            self.sequence_manager.add_sequence(step_number, animation_sequence)
            self.delete_temp_file(self.temp_animation_path)
            self.wait_for_response = False
            self.logger.add_log("Animation approved and saved.")
            return f"Animation saved successfully as step {step_number}.\n"

        elif user_input.lower() in ["n", "no"]:
            self.delete_temp_file(self.temp_animation_path)
            self.wait_for_response = False
            self.logger.add_log("Animation discarded by user.")
            return "Animation discarded.\n"

        self.logger.add_log(
            "Invalid response received during approval process.")
        return "Invalid response. Please reply with 'y' or 'n'.\n"

    def delete_temp_file(self, file_path):
        absolute_path = os.path.abspath(file_path)
        try:
            if os.path.exists(absolute_path):
                os.remove(absolute_path)
                if not os.path.exists(absolute_path):
                    self.logger.add_log(
                        f"Temp file {absolute_path} was successfully deleted.")
                else:
                    self.logger.add_log(
                        f"Error: Temp file {absolute_path} still exists after deletion attempt."
                    )
            else:
                self.logger.add_log(
                    f"Temp file {absolute_path} does not exist.")
        except Exception as e:
            self.logger.add_log(
                f"An error occurred while deleting {absolute_path}: {e}")
