from pydantic import BaseModel, Field, validator, ValidationError
from typing import List, Literal, Union, Optional, Dict, Any, Annotated, TypeVar, Generic
from typing_extensions import TypeAlias
import json  # Import the json module

# Generic type for framework-specific animation schema
T = TypeVar('T', bound=BaseModel)


# Action parameter models
class UpdateAnimationParams(BaseModel, Generic[T]):
    animation_sequence: T = Field(
        description=
        "The animation data to be processed - will be validated against framework-specific schema."
    )
    immediate_response: Literal[False] = Field(
        description=
        "Always False for update_animation as it requires user confirmation")


class GetAnimationParams(BaseModel):
    step_number: int = Field(
        description=
        "The step number of the animation to retrieve. If this parameter is missing, unknown to you or invalid (< 0), do not execute this action. Instead, use AskUserAction to ask the user for a valid step number.",
        ge=0)
    immediate_response: Literal[True] = Field(
        description="Always True for get_animation as it's a retrieval action")


class AddToMemoryParams(BaseModel):
    key: str = Field(
        description="The key under which to store the memory value")
    value: str = Field(description="The value to store in memory")
    immediate_response: Literal[False] = Field(
        description=
        "Always False for add_to_memory as it requires user confirmation")


class InformUserParams(BaseModel):
    message: str = Field(description="The message to send to the user")
    message_type: Literal["information", "answer", "error"] = Field(
        description=
        "The type of message being sent. Use 'information' for general info and success messages, 'answer' for answers to user questions, 'error' for error messages.",
        default="information")
    immediate_response: Literal[False] = Field(
        description=
        "Always False for inform_user as it's a one-way communication")


class AskUserParams(BaseModel):
    message: str = Field(description="The question or request for the user")
    message_type: Literal[
        "clarification", "question", "memory_suggestion"] = Field(
            description=
            "The type of message being sent. Use 'clarification' for input clarification, 'question' for general questions, 'memory_suggestion' when suggesting a memory entry.",
            default="question")
    immediate_response: Literal[False] = Field(
        description="Always False for ask_user as it requires user response")


# Action models with specific parameter types
class UpdateAnimationAction(BaseModel, Generic[T]):
    name: Literal["update_animation"]
    params: UpdateAnimationParams[T]


class GetAnimationAction(BaseModel):
    name: Literal["get_animation"]
    params: GetAnimationParams


class AddToMemoryAction(BaseModel):
    name: Literal["add_to_memory"]
    params: AddToMemoryParams


class AskUserAction(BaseModel):
    name: Literal["ask_user"]
    params: AskUserParams


# Union type for all possible actions
ActionType: TypeAlias = Annotated[Union[UpdateAnimationAction[T],
                                        GetAnimationAction, AddToMemoryAction,
                                        AskUserAction],
                                  Field(discriminator='name')]


# Updated schema to support single action execution with action planning
# This allows for more controlled execution while maintaining a clear plan of future actions
class MainSchema(BaseModel, Generic[T]):
    """
    Main schema that combines action handling with framework-specific animation schemas.
    The generic type T represents the framework-specific animation schema.
    """
    reasoning: str = Field(
        description=
        "A brief explanation of the reasoning behind the chosen action and the overall plan. High level plan of the animation journey. Be concise and to the point. Explain which of your available actions you will execute. Make sure you revise your previous plan in the reasoning fields."
    )
    # actions_plan: str = Field(
    #     description=
    #     "Write the planned actions, in bullet points,  to be executed in sequence in future turns. This plan can be revised in subsequent turns. Only mention which actions and with what order. No need to explain why. You explain why in the reasoning field.",
    #     default="")
    action: ActionType = Field(
        description="The single action to be executed in this turn. "
        "This field now supports both direct JSON objects and stringified JSON objects. "
        "If a string is provided, it will be parsed as JSON.")

    @validator('action', pre=True)
    def validate_action(cls, v):
        # If the input for 'action' is a string, attempt to parse it as JSON.
        # This allows the schema to accept stringified JSON from the LLM.
        if isinstance(v, str):
            try:
                parsed_v = json.loads(v)
                return parsed_v
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Action field is a string but not valid JSON: {e}") from e
        # If it's not a string (e.g., already a dictionary/object), return it as is.
        # Pydantic will then proceed with its normal validation against ActionType.
        return v

    @classmethod
    def with_framework_schema(
            cls, framework_schema: type[BaseModel]) -> type['MainSchema']:
        """
        Creates a new MainSchema class with the framework's schema.
        """

        class FrameworkMainSchema(cls[framework_schema]):
            pass

        return FrameworkMainSchema
