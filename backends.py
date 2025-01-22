import openai
import requests
from secrets import OPENAI_API_KEY, CLAUDE_API_KEY, GEMINI_API_KEY
from constants import API_TIMEOUT
from logger import Logger

class LLMBackend:
    """
    Base class for LLM backends.
    Each backend should inherit from this class and implement the generate_response method.
    """
    def __init__(self, name, logger):
        self.name = name
        self.logger = logger

    def generate_response(self, prompt):
        """Generate a response based on the provided prompt."""
        raise NotImplementedError("Subclasses must implement this method.")

    def log_tokens(self, prompt, response):
        """Log the number of tokens sent and received."""
        prompt_tokens = len(prompt.split())
        response_tokens = len(response.split())
        log_message = f"[{self.name}] Tokens sent: {prompt_tokens}, Tokens received: {response_tokens}"
        self.logger.add_message(tag=f"{self.name} Token Log", content=log_message)

class GPTBackend(LLMBackend):
    def generate_response(self, prompt):
        """Generate a response using GPT backend."""
        try:
            openai.api_key = OPENAI_API_KEY
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=150
            )
            response_text = response.choices[0].text.strip()
            self.log_tokens(prompt, response_text)
            return response_text
        except Exception as e:
            return f"[GPT Error]: {str(e)}"

class ClaudeBackend(LLMBackend):
    def generate_response(self, prompt):
        """Generate a response using Claude backend."""
        try:
            response = requests.post(
                "https://api.claude.ai/v1/complete",
                json={"prompt": prompt, "max_tokens": 150},
                headers={"Authorization": f"Bearer {CLAUDE_API_KEY}"},
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            response_text = response.json().get("completion", "[Claude Error]: No response")
            self.log_tokens(prompt, response_text)
            return response_text
        except Exception as e:
            return f"[Claude Error]: {str(e)}"

class GeminiBackend(LLMBackend):
    def generate_response(self, prompt):
        """Generate a response using Gemini backend."""
        try:
            response = requests.post(
                "https://api.gemini.ai/v1/query",
                json={"query": prompt, "max_tokens": 150},
                headers={"Authorization": f"Bearer {GEMINI_API_KEY}"},
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            response_text = response.json().get("response", "[Gemini Error]: No response")
            self.log_tokens(prompt, response_text)
            return response_text
        except Exception as e:
            return f"[Gemini Error]: {str(e)}"

class StubBackend(LLMBackend):
    def generate_response(self, prompt):
        """Generate a response using Stub backend with a valid xLights sequence."""
        sequence = (
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
            "<xsequence BaseChannel=\"0\" ChanCtrlBasic=\"0\" ChanCtrlColor=\"0\" FixedPointTiming=\"1\" ModelBlending=\"true\">"
            "<head>"
            "<version>2024.19</version>"
            "</head>"
            "<steps>"
            "<step>"
            "<number>1</number>"
            "<animation>Simple Animation</animation>"
            "</step>"
            "</steps>"
            "</xsequence>"
        )
        response_text = f"[Stub-{self.name}]: Simulated response with new '{sequence}'"
        self.log_tokens(prompt, response_text)
        return response_text
