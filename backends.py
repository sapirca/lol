import openai
import requests
import anthropic
# import google.generativeai as genai
from secrets import OPENAI_API_KEY, CLAUDE_API_KEY, GEMINI_API_KEY

GPT_4O_MINI_API_URL = "https://api.example.com/gpt-4o-mini"


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
    GPT_MODELS = {
        "gpt-4o-mini": 0.03,
        "gpt-4": 0.06,
        "gpt-4o": 0.035,
        "gpt-o1": 0.02,
        "gpt-o1-mini": 0.015
    }

    def __init__(self, logger, model="gpt-4o-mini"):
        super().__init__("GPT", logger)
        self.api_key = OPENAI_API_KEY
        self.api_url = GPT_4O_MINI_API_URL
        self.model = model
        self.logger.add_log(f"Using GPT model: {self.model}")

        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_response(self, messages):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "messages": messages,
        }
        try:
            completion = self.client.chat.completions.create(model=self.model,
                                                             messages=messages)

            print("Assistant: " + completion.choices[0].message.content)

            response_text = completion.choices[0].message.content.strip()
            self.log_tokens(messages, response_text)
            return response_text
        except Exception as e:
            self.logger.error(f"Error communicating with GPT API: {e}")
            print(f"Error communicating with GPT: {e}")


class ClaudeBackend(LLMBackend):  # Assuming LLMBackend is defined elsewhere

    CLAUDE_MODELS = {
        "claude-2": 0.05,
        "claude-instant": 0.025,
        "claude-next-gen": 0.03,
        "claude-lite": 0.015,
        "claude-ultra": 0.045,
        "claude-supernova": 0.055,
        "claude-3-5-sonnet-20241022":
        0.055  # Example price - add others as needed.
    }

    def __init__(self, logger, model="claude-3-5-sonnet-20241022"):
        super().__init__("Claude", logger)
        self.api_key = CLAUDE_API_KEY  # No longer needs to be an argument
        self.model = model
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.logger.add_log(f"Using Claude model: {self.model}")

        if self.model not in self.CLAUDE_MODELS:
            self.logger.add_log(
                f"Warning: Model {self.model} not found in CLAUDE_MODELS.")

    def generate_response(self, messages):
        """
        Communicates with the Claude backend.

        Args:
            messages (list): The array of messages to send to Claude.  Should follow
                             the Anthropic messages format.

        Returns:
            str: The response from Claude, or an error message.
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0,
                system=
                "You are a world-class poet. Respond only with short poems.",
                messages=messages)

            # Correct way to extract text content (handling content blocks):
            response_text = ""
            for content_block in response.content:
                if content_block.type == "text":
                    response_text += content_block.text
            response_text = response_text.strip()  # Clean up whitespace

            self.log_tokens(messages,
                            response_text)  # Assuming this function exists
            return response_text

        except anthropic.APIConnectionError as e:
            error_msg = f"Error connecting to Claude: {e}"
            self.logger.add_log(error_msg)  # Use the logger
            return f"Error: {error_msg}"  # Return the error message
        except anthropic.APIStatusError as e:
            error_msg = f"Claude API Error: {e}"
            self.logger.add_log(error_msg)
            return f"Error: {error_msg}"
        except Exception as e:  # Catch general exceptions
            error_msg = f"An unexpected error occurred: {e}"
            self.logger.add_log(error_msg)
            return f"Error: {error_msg}"


class GeminiBackend(LLMBackend):
    GEMINI_MODELS = {
        "gemini-1.5-flash-8b": 0.0375,
        "gemini-1.5-flash": 0.075,
        "gemini-1.5-pro": 1.25
    }

    def __init__(self, logger, model="gemini-1.5-flash"):
        super().__init__("Gemini", logger)
        self.api_key = GEMINI_API_KEY
        self.model = model
        self.logger.add_log(f"Using Gemini model: {self.model}")

        # genai.configure(api_key=self.api_key)
        # self.gemini_model = genai.GenerativeModel(self.model)

        self.gemini_model = None

    def generate_response(self, messages):
        """
        Communicates with the Gemini backend.

        Args:
            messages (list): The array of messages to send to Gemini.

        Returns:
            str: The response from Gemini.
        """
        try:
            prompt = "\n".join(
                [message["role"] + message["content"] for message in messages])
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text.strip()
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
