from pydantic import BaseModel, Field, ValidationError
import os
import litellm
import logging
from typing import List, Dict, Union, Type
from lol_secrets import OPENAI_API_KEY, CLAUDE_API_KEY, GEMINI_API_KEY
import json

litellm._turn_on_debug()

class LLMBackend:
    """
    Base class for LLM backends.
    Each backend should inherit from this class and implement the generate_response method.
    """

    def __init__(self,
                 name: str,
                 response_schema_obj: Type[BaseModel],
                 model: str,
                 config: Dict = None):
        self.name = name
        self.logger = logging.getLogger(name)
        self.config = config or {}
        self.model = model
        self.max_tokens = self.config.get("max_tokens", 4096)
        self.temperature = self.config.get("temperature", 0.5)
        self.logger.info(f"Using {name} model: {self.model}")
        self.response_schema_obj = response_schema_obj
        self.api_key = None

        if "gpt-" in model or "openai" in model:
            self.api_key = OPENAI_API_KEY
        elif "claude" in model or "anthropic" in model:
            self.api_key = CLAUDE_API_KEY
        elif "gemini" in model:
            self.api_key = GEMINI_API_KEY
        else:
            raise ValueError(f"Unsupported model: {model}")

    def generate_response(self, messages: List[Dict[str, str]]) -> BaseModel:
        """Generate a response based on the provided messages array and Pydantic schema."""
        try:
            # Add the Pydantic schema to the user's instructions
            schema_str = json.dumps(self.response_schema_obj.model_json_schema(), indent=2)
            updated_messages = messages + [
                {
                    "role": "user",
                    "content": f"Please respond with a JSON object that adheres to the following schema:\n\n{schema_str}"
                }
            ]

            response = litellm.completion(
                model=self.model,
                messages=updated_messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"},
                api_key=self.api_key
            )
            self.log_tokens(messages, response.choices[0].message.content)
            return self._parse_response(response.choices[0].message.content)

        except Exception as e:
            self.logger.error(f"Error communicating with LLM API ({self.name}): {e}")
            raise e

    def _parse_response(self, response_content: str) -> BaseModel:
        """Parses the JSON response and validates it against the Pydantic schema."""
        try:
            if response_content:
                json_output = json.loads(response_content)
                return self.response_schema_obj(**json_output)
            else:
                raise ValueError("Empty response content received from LLM.")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON response: {e}\nRaw Response: {response_content}")
            raise
        except ValidationError as e:
            self.logger.error(f"Pydantic validation error: {e}\nRaw Response: {response_content}")
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during response parsing: {e}\nRaw Response: {response_content}")
            raise

    def log_tokens(self, messages: List[Dict[str, str]], response: str):
        """Log the number of tokens sent and received."""
        try:
            prompt_tokens = litellm.token_counter(model=self.model, messages=messages)
            response_tokens = litellm.token_counter(model=self.model, messages=[{"content": response}])
            log_message = f"[{self.name}] Tokens sent: {prompt_tokens}, Tokens received: {response_tokens}"
            self.logger.info(log_message)
        except Exception as e:
            self.logger.warning(f"Error counting tokens: {e}")

    def token_count(self, messages: List[Dict[str, str]]) -> int:
        """
        Token counting method using LiteLLM's utility.
        """
        try:
            return litellm.token_counter(model=self.model, messages=messages)
        except Exception as e:
            self.logger.warning(f"Error counting tokens: {e}.  Using a rough estimate.")
            return sum(len(message["content"].split()) for message in messages)


# *************************************** #
# ***************** GPT ***************** #
class GPTBackend(LLMBackend):
    def __init__(self,
                 name,
                 response_schema_obj: Type[BaseModel],
                 model="gpt-4o-2024-08-06",
                 config: Dict = None):
        super().__init__(name=name,
                         response_schema_obj=response_schema_obj,
                         model=model,
                         config=config)


# *************************************** #
# **************** Claude *************** #
class ClaudeBackend(LLMBackend):
    def __init__(self,
                 name,
                 response_schema_obj: Type[BaseModel],
                 model="claude-3-7-sonnet-latest",
                 config: Dict = None):
        super().__init__(name=name,
                         response_schema_obj=response_schema_obj,
                         model=model,
                         config=config)


# *************************************** #
# **************** Gemini *************** #
# *************************************** #
class GeminiBackend(LLMBackend):
    def __init__(self,
                 name,
                 response_schema_obj: Type[BaseModel],
                 model="gemini/gemini-pro",
                 config: Dict = None):
        super().__init__(name=name,
                         response_schema_obj=response_schema_obj,
                         model=model,
                         config=config)
