import logging

import anthropic
import instructor
import openai
import tiktoken
from lol_secrets import OPENAI_API_KEY, CLAUDE_API_KEY, GEMINI_API_KEY
from pydantic import BaseModel, ValidationError
from instructor.exceptions import InstructorRetryException
import google.generativeai as genai

MAX_RETRIES = 3
INSTRACTOR_RETRIES = 3


class LLMBackend:
    """
    Base class for LLM backends.
    Each backend should inherit from this class and implement the generate_response method.
    """

    def __init__(self,
                 name,
                 response_schema_obj: BaseModel,
                 model,
                 mak_tokens,
                 config=None):
        self.name = name
        self.logger = logging.getLogger(name)
        self.config = config or {}
        self.model = model
        self.max_tokens = mak_tokens

        self.temperature = self.config.get("temperature", 0.5)
        self.response_schema_obj = response_schema_obj
        self.intstructor_response = self.config.get("instructor_response",
                                                    False)

        self.logger.info(f"Using {name} model: {self.model}")

    def generate_response(self, messages) -> BaseModel:
        raise NotImplementedError("Subclasses must implement this method.")

    def log_tokens(self, messages, response):
        prompt_tokens = self.token_count(messages)
        response_tokens = self.token_count([{"content": response}])
        self.logger.info(
            f"[{self.name}] Tokens sent: {prompt_tokens}, Tokens received: {response_tokens}"
        )

    def token_count(self, messages):
        return sum(len(message["content"].split()) for message in messages)


class GPTBackend(LLMBackend):
    """Implementation of LLMBackend for GPT models."""

    def __init__(self,
                 name,
                 response_schema_obj: BaseModel,
                 model="gpt-4o-2024-08-06",
                 mak_tokens=16384,
                 config=None):
        super().__init__(name=name,
                         response_schema_obj=response_schema_obj,
                         model=model,
                         mak_tokens=mak_tokens,
                         config=config)

        try:
            self.client = instructor.from_openai(
                openai.OpenAI(api_key=OPENAI_API_KEY))
        except Exception as e:
            self.logger.error(f"Error initializing OpenAI client: {e}")
            raise

    def generate_response(self, messages) -> BaseModel:
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    response_model=self.response_schema_obj,
                    max_retries=INSTRACTOR_RETRIES,
                )
                return response
            except (ValidationError, InstructorRetryException) as e:
                self.logger.warning(
                    f"\n\nValidation failed on attempt {attempt + 1}: {e}")
                error_message = f"The previous response did not match the expected schema. Error: {e}"
                messages = messages + [{
                    "role": "system",
                    "content": error_message
                }]
            except Exception as e:
                self.logger.error(
                    f"Error communicating with GPT API on attempt {attempt + 1}: {e}"
                )
                raise

        raise RuntimeError("Max retries exceeded for GPT response generation.")

    def token_count(self, messages):
        try:
            encoding = tiktoken.encoding_for_model(self.model)
            return sum(
                len(encoding.encode(message["content"]))
                for message in messages)
        except Exception as e:
            self.logger.warning(
                f"Error counting tokens with tiktoken. Using word split: {e}")
            return super().token_count(messages)


class ClaudeBackend(LLMBackend):
    """Implementation of LLMBackend for Claude models."""

    def __init__(self,
                 name,
                 response_schema_obj: BaseModel,
                 model="claude-3-5-sonnet-latest",
                 mak_tokens=64000,
                 config=None):
        super().__init__(name=name,
                         response_schema_obj=response_schema_obj,
                         model=model,
                         mak_tokens=mak_tokens,
                         config=config)

        try:
            self.client = instructor.from_anthropic(
                anthropic.Anthropic(api_key=CLAUDE_API_KEY))
        except Exception as e:
            self.logger.error(f"Error initializing Anthropic client: {e}")
            raise

    def generate_response(self, messages) -> BaseModel:
        system_messages = [
            m["content"] for m in messages if m["role"] == "system"
        ]
        chat_messages = [{
            "role": m["role"],
            "content": m["content"]
        } for m in messages if m["role"] != "system"]

        if system_messages:
            system_prompt = "\n".join(system_messages)
            if chat_messages:
                chat_messages[0][
                    "content"] = f"{system_prompt}\n{chat_messages[0]['content']}"
            else:
                chat_messages = [{"role": "user", "content": system_prompt}]

        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    messages=chat_messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    response_model=self.response_schema_obj,
                    max_retries=INSTRACTOR_RETRIES,
                )
                return response
            except ValidationError as e:
                self.logger.warning(
                    f"Validation failed on attempt {attempt + 1}: {e}")
                error_message = f"The previous response did not match the expected schema. Error: {e}"
                chat_messages = chat_messages + [{
                    "role": "user",
                    "content": error_message
                }]
            except Exception as e:
                self.logger.error(
                    f"Error communicating with Claude API on attempt {attempt + 1}: {e}"
                )
                raise

        raise RuntimeError(
            "Max retries exceeded for Claude response generation.")

    def token_count(self, messages):
        try:
            return super().token_count(messages)
        except Exception as e:
            self.logger.warning(
                f"Error counting tokens with fallback method: {e}")
            return super().token_count(messages)


class GeminiBackend(LLMBackend):
    """Implementation of LLMBackend for Gemini models."""

    def __init__(self,
                 name,
                 response_schema_obj: BaseModel,
                 model="models/gemini-1.5-pro-latest",
                 mak_tokens=64000,
                 config=None):
        super().__init__(name=name,
                         response_schema_obj=response_schema_obj,
                         model=model,
                         mak_tokens=mak_tokens,
                         config=config)

        try:
            genai.configure(
                api_key=GEMINI_API_KEY)  # Moved API key configuration here.

            self.client = instructor.from_gemini(
                client=genai.GenerativeModel(model_name=model, ),
                mode=instructor.Mode.GEMINI_JSON,
            )

        except Exception as e:
            self.logger.error(f"Error initializing Gemini client: {e}")
            raise

    def generate_response(self, messages) -> BaseModel:
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.messages.create(
                    messages=messages,
                    response_model=self.response_schema_obj,
                    max_retries=INSTRACTOR_RETRIES)
                return response
            except ValidationError as e:
                self.logger.warning(
                    f"Validation failed on attempt {attempt + 1}: {e}")
                error_message = f"The previous response did not match the expected schema. Error: {e}"
                messages = messages + [{
                    "role": "user",
                    "content": error_message
                }]
            except Exception as e:
                self.logger.error(
                    f"Error communicating with Gemini API on attempt {attempt + 1}: {e}"
                )
                raise

        raise RuntimeError(
            "Max retries exceeded for Gemini response generation.")

    def token_count(self, messages):
        try:
            return super().token_count(messages)
        except Exception as e:
            self.logger.warning(
                f"Error counting tokens with fallback method: {e}")
            return super().token_count(messages)
