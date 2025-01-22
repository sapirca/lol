import random
from backends import GPTBackend, ClaudeBackend, GeminiBackend, StubBackend, LLMBackend
from prompts import get_full_prompt
import xml.etree.ElementTree as ET
from chat_history import ChatHistory
from sequence_manager import SequenceManager
from constants import XSEQUENCE_TAG, ANIMATION_OUT_TEMP_DIR
from response_manager import ResponseManager
import os
from datetime import datetime

class MainController:
    def __init__(self, config):
        self.backends = {}
        self.use_stub = config.get("use_stub", False)
        self.selected_backend = config.get("selected_backend", None)
        self.chat_history = ChatHistory()
        self.initial_prompt_added = False
        self.house_config = self._load_house_config()
        self.sequence_manager = SequenceManager("sequence_skeleton.xml")
        self.response_manager = ResponseManager(self.sequence_manager)
        self.log_file = self._initialize_log()
        self.wait_for_response = False
        self.temp_animation_path = None
        self._initialize_backends()

    def _initialize_backends(self):
        backend_mapping = {
            "GPTBackend": GPTBackend,
            "ClaudeBackend": ClaudeBackend,
            "GeminiBackend": GeminiBackend,
            "StubBackend": StubBackend
        }
        for backend_name, backend_class in backend_mapping.items():
            self.register_backend(backend_class(backend_name))

    def _initialize_log(self):
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_filename = os.path.join(log_dir, datetime.now().strftime("conversation_log_%Y-%m-%d_%H-%M-%S.txt"))
        return open(log_filename, "a")

    def _log_message(self, sender, message):
        self.log_file.write(f"{sender}: {message}\n\n")

    def register_backend(self, backend):
        if not isinstance(backend, LLMBackend):
            raise TypeError("backend must be an instance of LLMBackend.")
        self.backends[backend.name] = backend

    def select_backend(self):
        if not self.backends:
            raise ValueError("No backends available.")

        if self.use_stub:
            stub_backend = self.backends.get("StubBackend")
            if not stub_backend:
                raise ValueError("StubBackend is not registered.")
            return stub_backend

        if self.selected_backend:
            selected_backend = self.backends.get(self.selected_backend)
            if selected_backend:
                return selected_backend

            print(f"Warning: Selected backend '{self.selected_backend}' not found, choosing randomly.")

        return random.choice(list(self.backends.values()))

    def _load_house_config(self):
        try:
            tree = ET.parse('house_config.xml')
            root = tree.getroot()
            return ET.tostring(root, encoding='unicode')
        except Exception as e:
            return f"Error loading house configuration: {e}"

    def communicate(self, user_input):
        if self.wait_for_response:
            return self.handle_user_approval(user_input)

        backend = self.select_backend()

        latest_sequence = self.sequence_manager.get_latest_sequence()

        if not self.initial_prompt_added:
            initial_prompt = get_full_prompt(self.house_config)
            self.chat_history.add_message("system", initial_prompt)
            self._log_message("system", initial_prompt)
            self.initial_prompt_added = True
        
        self.chat_history.add_message("user", user_input)
        self._log_message("user", user_input)

        prompt = self.chat_history.get_context() + f"\n\nAnimation Sequence ({XSEQUENCE_TAG}) is:\n\n{latest_sequence}"
        response = backend.generate_response(prompt)

        self.chat_history.add_message("assistant", response)
        self._log_message("assistant", response)

        parsed_response = self.response_manager.parse_response(response)

        return self.act_on_response(parsed_response)

    def act_on_response(self, processed_response):
        reasoning = processed_response.get("reasoning")
        consistency_justification = processed_response.get("consistency_justification")
        animation_sequence = processed_response.get("animation_sequence")

        output = ""

        if animation_sequence:
            output_dir = ANIMATION_OUT_TEMP_DIR
            os.makedirs(output_dir, exist_ok=True)

            temp_file_path = os.path.join(output_dir, "temp_animation.xml")
            self.temp_animation_path = os.path.abspath(temp_file_path)

            with open(self.temp_animation_path, "w") as temp_file:
                temp_file.write(animation_sequence)

            self.wait_for_response = True

            output += f"The animation has been stored in {self.temp_animation_path}.\n"
            output += "For the full reasoning and consistency, see log file.\n"
            output += "Simulate the file in xlight, edit and update the animation.\n"
            output += "Approve to save this animation to the sequence manager? (y/n): "

        else:
            output += "No animation sequence provided in the llm response.\n"

        actions = []
        for action in processed_response.get("requested_actions", []):
            actions.append({"action": action["action"], "content": action["content"]})
            output += f"Unhandled action: {action['action']}\n"

        return output

    def handle_user_approval(self, user_input):
        if user_input.lower() in ["y", "yes"]:
            step_number = len(self.sequence_manager.steps) + 1
            with open(self.temp_animation_path, "r") as temp_file:
                animation_sequence = temp_file.read()
            self.sequence_manager.add_sequence(step_number, animation_sequence)
            self.delete_temp_file(self.temp_animation_path)
            self.wait_for_response = False
            return f"Animation saved successfully as step {step_number}.\n"

        elif user_input.lower() in ["n", "no"]:
            self.delete_temp_file(self.temp_animation_path)
            self.wait_for_response = False
            return "Animation discarded.\n"

        return "Invalid response. Please reply with 'y' or 'n'.\n"

    def delete_temp_file(self, file_path):
        absolute_path = os.path.abspath(file_path)
        try:
            if os.path.exists(absolute_path):
                os.remove(absolute_path)
                if not os.path.exists(absolute_path):
                    self._log_message("system", f"Temp file {absolute_path} was successfully deleted.")
                else:
                    self._log_message("system", f"Error: Temp file {absolute_path} still exists after deletion attempt.")
            else:
                self._log_message("system", f"Temp file {absolute_path} does not exist. No deletion necessary.")
        except PermissionError:
            self._log_message("system", f"Permission denied while trying to delete {absolute_path}.")
        except FileNotFoundError:
            self._log_message("system", f"File {absolute_path} not found during deletion.")
        except Exception as e:
            self._log_message("system", f"An unexpected error occurred while deleting {absolute_path}: {e}")