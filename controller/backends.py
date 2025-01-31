import openai
import tiktoken
import anthropic
import google.generativeai as genai
import logging
#TODO sapir rename this file 
from secrets import OPENAI_API_KEY, CLAUDE_API_KEY, GEMINI_API_KEY

GPT_4O_MINI_API_URL = "https://api.example.com/gpt-4o-mini"


class LLMBackend:
    """
    Base class for LLM backends.
    Each backend should inherit from this class and implement the generate_response method.
    """

    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(name)

    def generate_response(self, messages):
        """Generate a response based on the provided messages array."""
        raise NotImplementedError("Subclasses must implement this method.")

    def log_tokens(self, messages, response):
        """Log the number of tokens sent and received."""
        prompt_tokens = self.token_count(messages)
        response_tokens = self.token_count([{"content": response}])
        log_message = f"[{self.name}] Tokens sent: {prompt_tokens}, Tokens received: {response_tokens}"
        self.logger.info(log_message)
    #     self.logger.add_message(tag=f"system_log {self.name} - Tokens",
    #                             content=log_message,
    #                             visible=False,
    #                             context=False)

    def token_count(self, messages):
        """Default token counting method using word splits."""
        return sum(len(message["content"].split()) for message in messages)


class GPTBackend(LLMBackend):
    GPT_MODELS = {
        "gpt-4o-mini": 0.03,
        "gpt-4": 0.06,
        "gpt-4o": 0.035,
        "gpt-o1": 0.02,
        "gpt-o1-mini": 0.015
    }

    def __init__(self, name, model="gpt-4o-mini"):
        super().__init__(name)
        self.api_key = OPENAI_API_KEY
        self.model = model
        self.logger.info(f"Using GPT model: {self.model}")

        self.client = openai.OpenAI(api_key=self.api_key)

    def token_count(self, messages):
        encoding = tiktoken.encoding_for_model(self.model)
        return sum(
            len(encoding.encode(message["content"])) for message in messages)

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

            response_text = completion.choices[0].message.content.strip()

            self.log_tokens(messages, response_text)
            return response_text
        except Exception as e:
            self.logger.error(f"Error communicating with GPT API: {e}")
            return (f"Error communicating with GPT: {e}")


class ClaudeBackend(LLMBackend):
    CLAUDE_MODELS = {
        "claude-2": 0.05,
        "claude-instant": 0.025,
        "claude-next-gen": 0.03,
        "claude-lite": 0.015,
        "claude-ultra": 0.045,
        "claude-supernova": 0.055,
        "claude-3-5-sonnet-20241022": 0.055
    }

    def __init__(self, name, model="claude-3-5-sonnet-20241022"):
        super().__init__(name)
        self.api_key = CLAUDE_API_KEY
        self.model = model
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.logger.info(f"Using Claude model: {self.model}")

        if self.model not in self.CLAUDE_MODELS:
            self.logger.warning(
                f"Model {self.model} not found in CLAUDE_MODELS.")

    def generate_response(self, messages):
        """
        Communicates with the Claude backend.

        Args:
            messages (list): A list of Message objects to send to Claude. Each Message object
                            should have 'role' and 'content' attributes.

        Returns:
            str: The response from Claude, or an error message.
        """
        # Separate system messages and chat messages
        system_messages = []
        chat_messages = []
        for message in messages:
            if message['role'] == 'system':
                system_messages.append(message['content'])
            else:
                chat_messages.append({
                    'role': message['role'],
                    'content': message['content']
                })

        try:
            # Send the request to Claude's backend
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0,
                system=" ".join(system_messages).strip(
                ),  # Concatenate with space for clarity
                messages=chat_messages)

            # Parse and clean up response text
            response_text = ""
            for content_block in response.content:  # Assuming response.content is iterable
                if content_block.type == "text":
                    response_text += content_block.text
            response_text = response_text.strip()  # Clean up whitespace

            if hasattr(self, 'log_tokens'):
                self.log_tokens(messages, response_text)

            return response_text

        except Exception as e:
            # Handle and log errors
            error_message = f"Error communicating with Claude backend: {str(e)}"
            if hasattr(self, 'log_tokens'):
                self.log_tokens(messages, error_message)
            return error_message


class GeminiBackend(LLMBackend):
    GEMINI_MODELS = {
        "gemini-1.5-flash-8b": 0.0375,
        "gemini-1.5-flash": 0.075,
        "gemini-1.5-pro": 1.25
    }

    def __init__(self, name, model="gemini-1.5-flash"):
        super().__init__(name)
        self.api_key = GEMINI_API_KEY
        self.model = model
        genai.configure(api_key=self.api_key)
        self.gemini_model = genai.GenerativeModel(self.model)

    def generate_response(self, messages):
        try:
            prompt = "\n".join(
                [f'{msg["role"]}: {msg["content"]}' for msg in messages])
            # Replace with actual Gemini API call
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text.strip()
            self.log_tokens(messages, response_text)
            return response_text
        except Exception as e:
            self.logger.error(f"Error communicating with Gemini backend: {e}")
            return f"Error communicating with Gemini backend {e}"

class DeepSeekBackend(LLMBackend):
    DEEPSEEK_MODELS = {
        "deepseek-chat": 0.04,
        "deepseek-chat-pro": 0.08,
        "deepseek-reasoner": 0.06,
    }

def __init__(self, name, model="deepseek-chat"):
    super().__init__(name)
    self.api_key = "<DeepSeek API Key>"
    self.model = model
    self.client = openai.OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com/v1")
    self.logger.info(f"Using DeepSeek model: {self.model}")

def generate_response(self, messages):
    try:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False
        )
        response_text = response.choices[0].message.content.strip()
        self.log_tokens(messages, response_text)
        return response_text
    except Exception as e:
        self.logger.error(f"Error communicating with DeepSeek backend: {e}")
        return f"Error communicating with DeepSeek backend: {e}"


class StubBackend(LLMBackend):

    def __init__(self, name):
        super().__init__(name)

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
        # if False:
        # if True:
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
