import random
from backends import GPTBackend, ClaudeBackend, GeminiBackend, StubBackend, LLMBackend
from prompts import get_full_prompt
import xml.etree.ElementTree as ET
from chat_history import ChatHistory
from sequence_manager import SequenceManager
from constants import XSEQUENCE_TAG, ANIMATION_OUT_TEMP_DIR
from response_manager import ResponseManager
import os

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
        backend = self.select_backend()

        latest_sequence = self.sequence_manager.get_latest_sequence()

        if not self.initial_prompt_added:
            initial_prompt = get_full_prompt(self.house_config)
            self.chat_history.add_message("system", initial_prompt)
            self.initial_prompt_added = True
        
        self.chat_history.add_message("user", user_input)
        prompt = self.chat_history.get_context() + f"\n\nAnimation Sequence ({XSEQUENCE_TAG}) is:\n\n{latest_sequence}"
        response = backend.generate_response(prompt)
        # TODO(sapir) sequences --? Save the Sequence? Print the Sequence?  
        self.chat_history.add_message("assistant", response)
        parsed_response = self.response_manager.parse_response(response)

        info = self.act_on_response(parsed_response)
        return response + str(info)

    def act_on_response(self, processed_response):
        reasoning = processed_response.get("reasoning")
        consistency_justification = processed_response.get("consistency_justification")
        animation_sequence = processed_response.get("animation_sequence")

        sequence_saved = False
        actions = []

        if animation_sequence:
            output_dir = ANIMATION_OUT_TEMP_DIR
            os.makedirs(output_dir, exist_ok=True)

            temp_file_path = os.path.join(output_dir, "temp_animation.xml")
            absolute_path = os.path.abspath(temp_file_path)

            with open(absolute_path, "w") as temp_file:
                temp_file.write(animation_sequence)
            print(f"File is closed? {temp_file.closed}")

            user_input = input(f"""
    The animation has been stored in {absolute_path}.
    Animation Info:
    Reasoning: {reasoning or "N/A"}
    Consistency Justification: {consistency_justification or "N/A"}
    You can simulate or edit the file using xLights. 
    Once done, decide whether to save it as a new version in the sequence manager.
    Approve to save this animation to the sequence manager? (y/n): """).strip().lower()

            if user_input == "y":
                step_number = len(self.sequence_manager.steps) + 1
                self.sequence_manager.add_sequence(step_number, animation_sequence)
                sequence_saved = True
                print(f"Animation saved successfully as step {step_number}. Thanks!")
            else:
                print("Animation discarded.")
            
        self.delete_temp_file(temp_file_path)

        for action in processed_response.get("requested_actions", []):
            print(f"Unhandled action: {action['action']}")
            actions.append({"action": action["action"], "content": action["content"]})

        return {
            "sequence_saved": sequence_saved,
            "reasoning": reasoning,
            "consistency_justification": consistency_justification,
            "actions": actions
        }


    def delete_temp_file(self, file_path):
        absolute_path = os.path.abspath(file_path)
        try:
            print("Trying to delete temp file...")
            if os.path.exists(absolute_path):
                os.remove(absolute_path)
                if not os.path.exists(absolute_path):
                    print(f"Temp file {absolute_path} was successfully deleted.")
                else:
                    print(f"Error: Temp file {absolute_path} still exists after deletion attempt.")
            else:
                print(f"Temp file {absolute_path} does not exist. No deletion necessary.")
        except PermissionError:
            print(f"Permission denied while trying to delete {absolute_path}.")
        except FileNotFoundError:
            print(f"File {absolute_path} not found during deletion.")
        except Exception as e:
            print(f"An unexpected error occurred while deleting {absolute_path}: {e}")
