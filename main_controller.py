# /Users/sapir/repos/lol/backends.py
import openai
import requests
from secrets import OPENAI_API_KEY, CLAUDE_API_KEY, GEMINI_API_KEY
from constants import API_TIMEOUT

class LLMBackend:
    def __init__(self, name):
        self.name = name

    def generate_response(self, prompt):
        raise NotImplementedError("Subclasses must implement this method.")

class GPTBackend(LLMBackend):
    def generate_response(self, prompt):
        try:
            openai.api_key = OPENAI_API_KEY
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=150
            )
            return response.choices[0].text.strip()
        except Exception as e:
            return f"[GPT Error]: {str(e)}"

class ClaudeBackend(LLMBackend):
    def generate_response(self, prompt):
        try:
            response = requests.post(
                "https://api.claude.ai/v1/complete",
                json={"prompt": prompt, "max_tokens": 150},
                headers={"Authorization": f"Bearer {CLAUDE_API_KEY}"},
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            return response.json().get("completion", "[Claude Error]: No response")
        except Exception as e:
            return f"[Claude Error]: {str(e)}"

class GeminiBackend(LLMBackend):
    def generate_response(self, prompt):
        try:
            response = requests.post(
                "https://api.gemini.ai/v1/query",
                json={"query": prompt, "max_tokens": 150},
                headers={"Authorization": f"Bearer {GEMINI_API_KEY}"},
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            return response.json().get("response", "[Gemini Error]: No response")
        except Exception as e:
            return f"[Gemini Error]: {str(e)}"

class StubBackend(LLMBackend):
    def generate_response(self, prompt):
        return """<?xml version="1.0" encoding="UTF-8"?>
<xsequence BaseChannel="0" ChanCtrlBasic="0" ChanCtrlColor="0" FixedPointTiming="1" ModelBlending="true">
<head>
<version>2024.19</version>
</head>
<steps>
<step>
<number>1</number>
<animation>Simple Animation</animation>
</step>
</steps>
</xsequence>
"""

# /Users/sapir/repos/lol/config.py

config = {
    "use_stub": True,
    "selected_backend": "GPT"
}

# /Users/sapir/repos/lol/prompts.py

intro_prompt = """You are an AI assistant specializing in crafting light sequences that suit the played music. Your task is to generate a visually engaging light show for the provided song using the xLights software. You will analyze the provided EDM music and create an XSQ sequence file based on the given template.

### Objectives
1. **Analyze the song:** Thoroughly understand its structure, energy levels, and mood.
2. **Plan the animation journey:** Develop a high-level plan for your light show animation.
3. **Provide a runnable XSQ file:** Populate the "ElementEffects" section with xLights effects.
4. **Learn user preferences:** Note user-specific preferences for light effects.
5. **Explain the process:** Justify your design decisions in detail, wrapping the explanation inside `<reasoning>` tags.
6. **Utilize existing knowledge:** Use your understanding of xLights effects and user input.
7. **Promptly ask for user preferences when necessary.**
8. **Provide consistency justification:** Wrap consistency checks or clarifying questions inside `<consistency_justification>` tags.

### Response Format
- If generating a light sequence, include the **full xLights XML sequence** wrapped with the `<xsequence>` tag.
- For actions or other tasks, wrap the relevant data inside `<action_name>` and `</action_name>` tags.
- For explanations or reasoning, include the content inside `<reasoning>` and `</reasoning>` tags.
- For consistency justification, include content inside `<consistency_justification>` tags.

### Internal Format for Actions
- **store_to_memory**: Save the content for future context.
- **query_user**: Ask a clarifying question.

Ensure all outputs adhere to the above structure.
"""

song_information_prompt = """
Generate a light show for this song:
Song: "Nikki" by Worakls

BPM: 126

Song structure:
8 Bars: Intro
16 Bars: Verse 1
16 Bars: Verse 2
16 Bars: Bridge
16 Bars: Build up
16 Bars: Drop (chorus)
16 Bars: Verse
16 Bars: Bridge
16 Bars: Build up
16 Bars: Outro
"""

prompts_list = [song_information_prompt]

def get_full_prompt(house_config):
    return intro_prompt + "\n" + "\n".join(prompts_list) + f"\n\nHouse Configuration:\n{house_config}"


# /Users/sapir/repos/lol/main_controller.py
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

            output += "I have an updated animaion for you."
            output += f"The animation has been stored in {self.temp_animation_path}.\n"
            output += "For the full reasoning and consistency, see log file.\n"
            output += "Simulate the file in xlight, edit and update the animation.\n"
            output += "Approve to save this animation to the sequence manager? (y/n)"

        else:
            output += "No animation sequence provided in the llm response."

        actions = []
        for action in processed_response.get("requested_actions", []):
            actions.append({"action": action["action"], "content": action["content"]})
            output += f"Unhandled action: {action['action']}"

        return output

    def handle_user_approval(self, user_input):
        if user_input.lower() in ["y", "yes"]:
            step_number = len(self.sequence_manager.steps) + 1
            with open(self.temp_animation_path, "r") as temp_file:
                animation_sequence = temp_file.read()
            self.sequence_manager.add_sequence(step_number, animation_sequence)
            self.delete_temp_file(self.temp_animation_path)
            self.wait_for_response = False
            return f"Animation saved successfully as step {step_number}."

        elif user_input.lower() in ["n", "no"]:
            self.delete_temp_file(self.temp_animation_path)
            self.wait_for_response = False
            return "Animation discarded."

        return "Invalid response. Please reply with 'y' or 'n'."

    def delete_temp_file(self, file_path):
        absolute_path = os.path.abspath(file_path)
        try:
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

# /Users/sapir/repos/lol/response_manager.py
from constants import XSEQUENCE_TAG
import re

class ResponseManager:
    def __init__(self, sequence_manager):
        self.sequence_manager = sequence_manager

    def parse_response(self, response):
        result = {
            "reasoning": None,
            "animation_sequence": None,
            "requested_actions": [],
            "consistency_justification": None
        }

        if "<?xml" in response and f"</{XSEQUENCE_TAG}>" in response:
            sequence_start = response.find("<?xml")
            sequence_end = response.find(f"</{XSEQUENCE_TAG}>") + len(f"</{XSEQUENCE_TAG}>")
            sequence_xml = response[sequence_start:sequence_end]
            result["animation_sequence"] = sequence_xml

            response = response[:sequence_start] + response[sequence_end:]

        tags = re.findall(r"<([a-zA-Z0-9_]+)>(.*?)</\1>", response, re.DOTALL)
        for tag, content in tags:
            if tag == "reasoning":
                result["reasoning"] = content.strip()
            elif tag == "consistency_justification":
                result["consistency_justification"] = content.strip()
            else:
                result["requested_actions"].append({"action": tag, "content": content.strip()})

        return result