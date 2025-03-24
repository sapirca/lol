import instructor
import openai
import tiktoken
import anthropic
from google import genai
import logging
import json
from animation.frameworks.conceptual.response_schema import ResponseSchema
from animation.frameworks.kivsee.scheme.effects_p2p import ResponseProto
from lol_secrets import OPENAI_API_KEY, CLAUDE_API_KEY
from pydantic import BaseModel


class LLMBackend:
    """
    Base class for LLM backends.
    Each backend should inherit from this class and implement the generate_response method.
    """

    def __init__(self, name, response_object: BaseModel, model, config=None):
        self.name = name
        self.logger = logging.getLogger(name)
        self.config = config or {}
        self.model = model
        self.max_tokens = self.config.get("max_tokens", 2048)
        self.temperature = self.config.get("temperature", 0.5)
        self.logger.info(f"Using {name} model: {self.model}")
        self.intstructor_response = self.config.get("instructor_response",
                                                    False)
        self.response_schema_obj = response_object

    def generate_response(self, messages) -> BaseModel:
        """Generate a response based on the provided messages array."""
        raise NotImplementedError("Subclasses must implement this method.")

    def log_tokens(self, messages, response):
        """Log the number of tokens sent and received."""
        prompt_tokens = self.token_count(messages)
        response_tokens = self.token_count([{"content": response}])
        log_message = f"[{self.name}] Tokens sent: {prompt_tokens}, Tokens received: {response_tokens}"
        self.logger.info(log_message)

    def token_count(self, messages):
        """Default token counting method using word splits."""
        return sum(len(message["content"].split()) for message in messages)


# *************************************** #
# ***************** GPT ***************** #
# *************************************** #


class GPTBackend(LLMBackend):
    # gpt-4o-mini-2024-07-18
    # gpt-4o-2024-08-06
    def __init__(self, name, response_object: BaseModel, model="gpt-4o-2024-08-06", config=None):
        super().__init__(name=name, response_object=response_object, model=model, config=config)
        self.client = instructor.from_openai(openai.OpenAI(api_key=OPENAI_API_KEY))

    def generate_response(self, messages) -> BaseModel:
        data = {
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "model": self.model,
            "response_model": ResponseProto,
        }
        try:
            response = self.client.chat.completions.create(**data)
            return response
        except Exception as e:
            self.logger.error(f"Error communicating with GPT API: {e}")
            raise e


# *************************************** #
# **************** Claude *************** #
# *************************************** #

class ClaudeBackend(LLMBackend):

    def __init__(self, name, response_object: BaseModel, model="claude-3-5-sonnet-20241022", config=None):
        super().__init__(name=name, response_object=response_object, model=model, config=config)
        self.client = instructor.from_anthropic(
            client=anthropic.Anthropic(api_key=CLAUDE_API_KEY),
        )


    def generate_response(self, messages) -> BaseModel:
        system_messages = []
        chat_messages = []

        try:
            for message in messages:
                if message['role'] == 'system':
                    system_messages.append(message['content'])
                else:
                    chat_messages.append({
                        'role': message['role'],
                        'content': message['content']
                    })

            claude_messages = [{
                "role": chat_message["role"],
                "content": chat_message["content"]
            } for chat_message in chat_messages]

            system_prompt = "\n".join(
                system_messages) if system_messages else ""

            data = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "system":
                system_prompt,  # Correct usage of system instructions
                "messages": claude_messages,
                "response_model": ResponseProto,
            }
            response = self.client.messages.create(**data)
            return response

        except Exception as e:
            error_message = f"Error, Claude backend: {str(e)}"
            raise e

