import openai
import requests
from secrets import OPENAI_API_KEY, CLAUDE_API_KEY, GEMINI_API_KEY


class LLMBackend:
    """
    Base class for LLM backends.
    Each backend should inherit from this class and implement the generate_response method.
    """

    def __init__(self, name, logger):
        self.name = name
        self.logger = logger

    def generate_response(self, messages):
        """Generate a response based on the provided messages array."""
        raise NotImplementedError("Subclasses must implement this method.")

    def log_tokens(self, messages, response):
        """Log the number of tokens sent and received."""
        prompt_tokens = sum(
            len(message["content"].split()) for message in messages)
        response_tokens = len(response.split())
        log_message = f"[{self.name}] Tokens sent: {prompt_tokens}, Tokens received: {response_tokens}"
        self.logger.add_message(tag=f"system_log {self.name} - Tokens",
                                content=log_message,
                                visible=False,
                                context=False)


class GPTBackend(LLMBackend):

    def __init__(self, logger):
        super().__init__("GPT", logger)
        self.api_key = OPENAI_API_KEY

    def generate_response(self, messages):
        """
        Communicates with the GPT backend using OpenAI's API.

        Args:
            messages (list): The array of messages to send to GPT.

        Returns:
            str: The response from GPT.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-mini",  # Updated to use GPT-4o-mini
                messages=messages,
                max_tokens=150,
                api_key=self.api_key)
            response_text = response.choices[0].message.content.strip()
            self.log_tokens(messages, response_text)
            return response_text
        except Exception as e:
            print(f"Error communicating with GPT: {e}")
            return "Error: Unable to connect to GPT backend."


class ClaudeBackend(LLMBackend):

    def __init__(self, logger):
        super().__init__("Claude", logger)
        self.api_key = CLAUDE_API_KEY

    def generate_response(self, messages):
        """
        Communicates with the Claude backend.

        Args:
            messages (list): The array of messages to send to Claude.

        Returns:
            str: The response from Claude.
        """
        try:
            prompt = "\n".join([message["content"] for message in messages])
            url = "https://api.anthropic.com/v1/claude"  # Replace with the actual API endpoint
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {"prompt": prompt, "max_tokens": 150}
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_text = response.json().get("completion", "").strip()
            self.log_tokens(messages, response_text)
            return response_text
        except Exception as e:
            print(f"Error communicating with Claude: {e}")
            return "Error: Unable to connect to Claude backend."


class GeminiBackend(LLMBackend):

    def __init__(self, logger):
        super().__init__("Gemini", logger)
        self.api_key = GEMINI_API_KEY

    def generate_response(self, messages):
        """
        Communicates with the Gemini backend.

        Args:
            messages (list): The array of messages to send to Gemini.

        Returns:
            str: The response from Gemini.
        """
        try:
            prompt = "\n".join([message["content"] for message in messages])
            url = "https://api.gemini.com/v1/ai"  # Replace with the actual API endpoint
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {"input": prompt, "max_tokens": 150}
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_text = response.json().get("output", "").strip()
            self.log_tokens(messages, response_text)
            return response_text
        except Exception as e:
            print(f"Error communicating with Gemini: {e}")
            return "Error: Unable to connect to Gemini backend."


class StubBackend(LLMBackend):

    def __init__(self, logger):
        super().__init__("Stub", logger)

    def generate_response(self, messages):
        """
        Stub backend that returns a fixed response for testing purposes.

        Args:
            messages (list): The array of messages to process.

        Returns:
            str: A fixed response for testing, occasionally including an animation sequence.
        """
        import random

        response_text = "This is a stubbed response."

        # Randomly include an animation sequence in the response
        if random.choice([True, False]):
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
                "</xsequence>")
            response_text += f"\n{sequence}"

        self.log_tokens(messages, response_text)
        return response_text
