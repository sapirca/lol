import logging
from abc import ABC, abstractmethod

import anthropic
import instructor
import openai
import tiktoken  # Kept for potential fallback or other uses, but not for primary token logging
from lol_secrets import OPENAI_API_KEY, CLAUDE_API_KEY, GEMINI_API_KEY
from pydantic import BaseModel, ValidationError
from instructor.exceptions import InstructorRetryException
import google.generativeai as genai
from constants import MODEL_CONFIGS

MAX_RETRIES = 3
INSTRACTOR_RETRIES = 0


class LLMBackend(ABC):  # Inherit from ABC for abstract methods
    """
    Base class for LLM backends.
    Each backend should inherit from this class and implement the abstract methods.
    """

    def __init__(self, name, response_schema_obj: BaseModel, config=None):
        self.name = name
        self.logger = logging.getLogger(name)
        self.config = config or {}

        self.temperature = self.config.get("temperature", 0.5)
        self.response_schema_obj = response_schema_obj
        self.intstructor_response = self.config.get("instructor_response",
                                                    False)

    @abstractmethod
    def _make_api_call(self, messages):
        """
        Abstract method to perform the specific API call for the backend.
        Should return the raw API response object.
        """
        pass

    @abstractmethod
    def _get_token_counts(self, response):
        """
        Abstract method to extract prompt and completion token counts from the raw API response.
        Should return a tuple (prompt_tokens, completion_tokens).
        """
        pass

    def generate_response(self, messages) -> BaseModel:
        """
        Generates a response from the LLM, handling retries and validation.
        Logs token usage by calling _get_token_counts.
        """
        current_messages = list(
            messages)  # Create a mutable copy for appending error messages

        for attempt in range(MAX_RETRIES):
            try:
                # Perform the API call specific to the backend
                response = self._make_api_call(current_messages)

                # Extract and log token usage
                prompt_tokens, completion_tokens = self._get_token_counts(
                    response)
                if prompt_tokens is not None and completion_tokens is not None:
                    self.logger.info(
                        f"[{self.name}] Tokens sent: {prompt_tokens}, Tokens received: {completion_tokens}"
                    )
                else:
                    self.logger.warning(
                        f"[{self.name}] Could not retrieve token usage information from response."
                    )

                return response
            except (ValidationError, InstructorRetryException) as e:
                self.logger.warning(
                    f"\n\nValidation failed on attempt {attempt + 1}: {e}")
                # Append error message to messages for re-attempt
                error_message = f"The previous response did not match the expected schema. Error: {e}"
                # error_message += f"\n\n{response}"
                current_messages.append({
                    "role":
                    "system",  # Using 'system' role for error messages, adjust if 'user' is preferred by LLM
                    "content": error_message
                })
            except Exception as e:
                self.logger.error(
                    f"Error communicating with {self.name} API on attempt {attempt + 1}: {e}"
                )
                raise

        raise RuntimeError(
            f"Max retries exceeded for {self.name} response generation.")


class GPTBackend(LLMBackend):
    """Implementation of LLMBackend for GPT models."""

    def __init__(self, name, response_schema_obj: BaseModel, config=None):
        super().__init__(name=name,
                         response_schema_obj=response_schema_obj,
                         config=config)

        # Get model config from config or use default
        model_config = self.config.get("model_config", MODEL_CONFIGS["GPT"])
        self.model = model_config["model_name"]
        self.max_tokens = model_config["max_tokens"]

        self.logger.info(f"Using {name} model: {self.model}")

        try:
            self.client = instructor.from_openai(
                openai.OpenAI(api_key=OPENAI_API_KEY))
        except Exception as e:
            self.logger.error(f"Error initializing OpenAI client: {e}")
            raise

    def _make_api_call(self, messages):
        """
        Performs the OpenAI API call.
        """
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            response_model=self.response_schema_obj,
            max_retries=INSTRACTOR_RETRIES,
        )

    def _get_token_counts(self, response):
        """
        Extracts token counts from GPT API response.
        """
        if hasattr(response, 'usage') and response.usage:
            return response.usage.prompt_tokens, response.usage.completion_tokens
        return None, None


class ClaudeBackend(LLMBackend):
    """Implementation of LLMBackend for Claude models."""

    def __init__(self, name, response_schema_obj: BaseModel, config=None):
        super().__init__(name=name,
                         response_schema_obj=response_schema_obj,
                         config=config)

        # Get model config from config or use default
        model_config = self.config.get("model_config", MODEL_CONFIGS["Claude"])
        self.model = model_config["model_name"]
        self.max_tokens = model_config["max_tokens"]

        self.logger.info(f"Using {name} model: {self.model}")

        try:
            self.client = instructor.from_anthropic(
                anthropic.Anthropic(api_key=CLAUDE_API_KEY))
        except Exception as e:
            self.logger.error(f"Error initializing Anthropic client: {e}")
            raise

    def _make_api_call(self, messages):
        """
        Performs the Claude API call, handling system messages.
        """
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
                # Prepend system prompt to the first user message
                chat_messages[0][
                    "content"] = f"{system_prompt}\n{chat_messages[0]['content']}"
            else:
                # If only system messages, make them a user message for the API
                chat_messages = [{"role": "user", "content": system_prompt}]

        return self.client.messages.create(
            model=self.model,
            messages=chat_messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            response_model=self.response_schema_obj,
            max_retries=INSTRACTOR_RETRIES,
        )

    def _get_token_counts(self, response):
        """
        Extracts token counts from Claude API response.
        """
        if hasattr(response, 'usage') and response.usage:
            return response.usage.input_tokens, response.usage.output_tokens
        return None, None


class GeminiBackend(LLMBackend):
    """Implementation of LLMBackend for Gemini models."""

    def __init__(self, name, response_schema_obj: BaseModel, config=None):
        super().__init__(name=name,
                         response_schema_obj=response_schema_obj,
                         config=config)

        # Get model config from config or use default
        model_config = self.config.get("model_config", MODEL_CONFIGS["Gemini"])
        self.model = model_config["model_name"]
        self.max_tokens = model_config["max_tokens"]

        self.logger.info(f"Using {name} model: {self.model}")

        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.client = instructor.from_gemini(
                client=genai.GenerativeModel(model_name=self.model),
                mode=instructor.Mode.GEMINI_JSON,
            )
        except Exception as e:
            self.logger.error(f"Error initializing Gemini client: {e}")
            raise

    def _make_api_call(self, messages):
        """
        Performs the Gemini API call.
        """
        return self.client.messages.create(
            messages=messages,
            response_model=self.response_schema_obj,
            max_retries=INSTRACTOR_RETRIES)

    def _get_token_counts(self, response):
        """
        Extracts token counts from Gemini API response.
        """
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            return response.usage_metadata.prompt_token_count, response.usage_metadata.candidates_token_count
        return None, None
