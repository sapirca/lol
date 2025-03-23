import instructor
import openai
import tiktoken
import anthropic
from google import genai
import logging
import json
from lol_secrets import DEEP_SEEK_API_KEY, OPENAI_API_KEY, CLAUDE_API_KEY, GEMINI_API_KEY
from pydantic import BaseModel
from controller.response_schema import ResponseSchema
# from llama import LlamaClient  # Assuming there's a LlamaClient to import


class LLMBackend:
    """
    Base class for LLM backends.
    Each backend should inherit from this class and implement the generate_response method.
    """

    def __init__(self, name, model, config=None):
        self.name = name
        self.logger = logging.getLogger(name)
        self.config = config or {}
        self.model = model
        self.max_tokens = self.config.get("max_tokens", 2048)
        self.temperature = self.config.get("temperature", 0.5)
        self.logger.info(f"Using {name} model: {self.model}")
        self.intstructor_response = self.config.get("instructor_response",
                                                    False)
        self.w_structured_output = self.config.get("with_structured_output",
                                                   False)

    def generate_response(self, messages):
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


class StubBackend(LLMBackend):

    def __init__(self, name, config=None):
        super().__init__(name, "stub", config=config)

    def generate_response(self, messages):
        response_schema = ResponseSchema(
            name="stub_response",
            reasoning="This is a stubbed reasoning.",
            animation={
                "name": "stub_animation",
                "duration": 0,
                "beats": []
            })

        self.log_tokens(messages, response_schema.dict())
        return response_schema


# *************************************** #
# ***************** GPT ***************** #
# *************************************** #


class GPTBackend(LLMBackend):

    def __init__(self, name, model="gpt-4o-mini-2024-07-18", config=None):
        super().__init__(name, model, config=config)
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)

    def generate_response(self, messages):
        data = {
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "model": self.model,
            # "response_format": ResponseSchema
        }

        data["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "ResponseSchema",
                "schema": ResponseSchema.model_json_schema()
            }
        }

        try:
            # if self.intstructor_response:
            # response = self.client.beta.chat.completions.parse(**data)
            # response = response.choices[0].message.parsed

            # else:
            response = self.client.chat.completions.create(**data)
            response = response.choices[0].message.content.strip()
            return ResponseSchema(response)
        except Exception as e:
            self.logger.error(f"Error communicating with GPT API: {e}")
            raise e


# *************************************** #
# **************** Claude *************** #
# *************************************** #


class ClaudeBackend(LLMBackend):

    def __init__(self, name, model="claude-3-5-sonnet-20241022", config=None):
        super().__init__(name, model, config=config)
        self.client = instructor.from_anthropic(
            client=anthropic.Anthropic(api_key=CLAUDE_API_KEY),
            # model=self.model,
        )

        # self.client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    def generate_response(self, messages):
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
                "response_model": ResponseSchema,
            }
            completion = self.client.messages.create(**data)
            # response = completion.choices[0].message.content.strip()

            if hasattr(completion, 'content') and isinstance(
                    completion.content, list):
                result = completion.content[0].text
                parsed_result = json.loads(result)
                response = ResponseSchema(**parsed_result)
            else:
                # If response_model was accepted, result is already parsed
                response = completion

            return response

        except Exception as e:
            error_message = f"Error, Claude backend: {str(e)}"
            raise e


# *************************************** #
# **************** Gemini *************** #
# *************************************** #
class GeminiBackend(LLMBackend):

    def __init__(self, name, model="gemini-1.5-flash-latest", config=None):
        super().__init__(name, model, config=config)
        # genai.configure(api_key=GEMINI_API_KEY)
        # self.client = genai.GenerativeModel(model_name=self.model)
        self.api_key = GEMINI_API_KEY
        self.client = genai.Client(api_key=self.api_key)

    def generate_response(self, messages):
        try:
            prompt = "\n".join(
                [f'{msg["role"]}: {msg["content"]}' for msg in messages])
            schema = ResponseSchema.model_json_schema()
            prompt += "\nUse this JSON schema:" + json.dumps(schema)
            response = self.client.models.generate_content(model=self.model,
                                                           contents=prompt)
            response_text = response.text.strip()
            response_text = response_text.replace("```json",
                                                  "").replace("```",
                                                              "").strip()
            return response_text
        except Exception as e:
            self.logger.error(f"Error communicating with Gemini backend: {e}")
            raise e


# ***************************************** #
# ************** Deep Seek **************** #
# ***************************************** #


class DeepSeekBackend(LLMBackend):

    def __init__(self, name, model="deepseek-chat", config=None):
        super().__init__(name, model, config=config)
        self.client = instructor.from_openai(
            openai.OpenAI(api_key=DEEP_SEEK_API_KEY,
                          base_url="https://api.deepseek.com"))

    def generate_response(self, messages):
        try:
            schema = ResponseSchema.model_json_schema()
            data = {
                "model": self.model,
                "messages": messages,
                "response_model": ResponseSchema,
            }

            response = self.client.chat.completions.create(**data)

            # TODO Sapir RTokens
            # response, completion = self.client.chat.completions.create_with_completion(
            # print(completion.usage)
            return response
        except Exception as e:
            self.logger.error(
                f"Error communicating with DeepSeek backend: {e}")
            raise e


# ***************************************** #
# **************** Llama ****************** #
# ***************************************** #

# class LlamaBackend(LLMBackend):

#     def __init__(self, name, model="llama-2-7b-chat", config=None):
#         super().__init__(name, model, config=config)
#         self.client = LlamaClient(api_key=LLAMA_API_KEY)

#     def generate_response(self, messages):
#         try:
#             schema = ResponseSchema.model_json_schema()
#             data = {
#                 "model": self.model,
#                 "messages": messages,
#                 "response_model": ResponseSchema,
#             }

#             response = self.client.chat.completions.create(**data)
#             return response
#         except Exception as e:
#             self.logger.error(f"Error communicating with Llama backend: {e}")
#             raise e

# ***************************************** #
# *************** TogetherAI ************** #
# ***************************************** #


class TogetherAIBackend(LLMBackend):

    def __init__(self, name, model="together-gpt", config=None):
        super().__init__(name, model, config=config)
        self.api_key = self.config.get("together_api_key")
        if not self.api_key:
            raise ValueError("TogetherAI API key is required.")
        self.client = instructor.from_openai(
            openai.OpenAI(api_key=self.api_key,
                          base_url="https://api.together.ai"))

    def generate_response(self, messages):
        try:
            schema = ResponseSchema.model_json_schema()
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "stop": ["<|im_end|>", "<|endoftext|>"],
                "response_model": ResponseSchema,
            }

            response = self.client.chat.completions.create(**data)
            return response
        except Exception as e:
            self.logger.error(
                f"Error communicating with TogetherAI backend: {e}")
            raise e
