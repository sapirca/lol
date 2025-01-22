
# main_controller.py
import random
from backends import GPTBackend, ClaudeBackend, GeminiBackend, StubBackend, LLMBackend
from prompts import get_full_prompt
import xml.etree.ElementTree as ET
from sequence_manager import SequenceManager
from response_manager import ResponseManager
from constants import XSEQUENCE_TAG, ANIMATION_OUT_TEMP_DIR
from logger import Logger
import os


class MainController:
    def __init__(self, config):
        self.backends = {}
        self.use_stub = config.get("use_stub", False)
        self.selected_backend = config.get("selected_backend", None)
        self.house_config = self._load_house_config()
        self.sequence_manager = SequenceManager("sequence_skeleton.xml")
        self.response_manager = ResponseManager(self.sequence_manager)
        self.logger = Logger()
        self.initial_prompt_added = False
        self.wait_for_response = False
        self.temp_animation_path = None
        self._initialize_backends()

    def shutdown(self):
        self.logger.finalize()
        print("Session finalized. Logs saved.")

    def _initialize_backends(self):
        backend_mapping = {
            "GPTBackend": GPTBackend,
            "ClaudeBackend": ClaudeBackend,
            "GeminiBackend": GeminiBackend,
            "StubBackend": StubBackend
        }
        for backend_name, backend_class in backend_mapping.items():
            self.register_backend(backend_class(backend_name, self.logger))


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
          self.logger.add_message("lol_visible_user", user_input)
          visible_system_message = self.handle_user_approval(user_input)
          self.logger.add_message("lol_visible_system", visible_system_message)
          return {"system": visible_system_message}

        backend = self.select_backend()

        latest_sequence = self.sequence_manager.get_latest_sequence()

        if not self.initial_prompt_added:
            initial_prompt = get_full_prompt(self.house_config)
            self.logger.add_message("lol_inital_prompt_context","System: " + initial_prompt)
            self.logger.add_message("lol_animation", latest_sequence)  # Log initial animation
            self.initial_prompt_added = True

        
        self.logger.add_message("lol_visible_user_context", "User: " + user_input)

        # Construct the full prompt for the LLM
        prompt = self.logger.get_context_to_llm() + f"\n\nAnimation Sequence ({XSEQUENCE_TAG}) is:\n\n{latest_sequence}"
        self.logger.add_message("lol_system_final_prompt", prompt)
        response = backend.generate_response(prompt)
        self.logger.add_message("lol_raw_response", response)

        parsed_response = self.response_manager.parse_response(response)

        assistant_response = parsed_response.get("response_wo_animation", "")
        self.logger.add_message("lol_visible_assistant_context", "Assistant: " + assistant_response + "The animationed was trimmed out")

        system_response = self.act_on_response(parsed_response)
        self.logger.add_message("lol_visible_system", system_response)

        return {
            "assistant": assistant_response,
            "system": system_response
        }

    def act_on_response(self, processed_response):
        reasoning = processed_response.get("reasoning")
        consistency_justification = processed_response.get("consistency_justification")
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

            self.logger.add_message("lol_system", "generated temp_animation.xml for the user's observation")
            self.wait_for_response = True

            output += f"An animation sequence was generated and saved in  {self.temp_animation_path}.\n"
            output += "Simulate or edit the file using xLights. Edit the animation file in needed.\n"
            output += " Approve to save this animation to the sequence manager once done. Approve? (y/n): "

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
            self.logger.add_message("lol_animation", animation_sequence) # log every sequence update
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
                    self.logger.add_message("lol_system", f"Temp file {absolute_path} was successfully deleted.")
                else:
                    self.logger.add_message("lol_system", f"Error: Temp file {absolute_path} still exists after deletion attempt.")
            else:
                self.logger.add_message("lol_system", f"Temp file {absolute_path} does not exist.")
        except Exception as e:
            self.logger.add_message("lol_system", f"An error occurred while deleting {absolute_path}: {e}")