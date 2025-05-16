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
    immediate_response: bool = Field(
        description=
        "Should always be False for update_animation as it requires user confirmation",
        default=False)


class GetAnimationParams(BaseModel):
    step_number: int = Field(
        description=
        "The step number of the animation to retrieve. If this parameter is missing, unknown to you or invalid (< 0), do not execute this action. Instead, use ResponseToUserAction with message_type='clarification' to ask the user for a valid step number.",
        ge=0)
    immediate_response: bool = Field(
        description=
        "Should always be True for get_animation as it's a retrieval action that doesn't need user input",
        default=True)


class GetMemoryParams(BaseModel):
    immediate_response: bool = Field(
        description=
        "Should always be True for get_memory as it's a retrieval action that doesn't need user input",
        default=True)


class GetMusicStructureParams(BaseModel):
    song_name: str = Field(
        description=
        "Name of the song to get structure for. If this parameter is missing, do not execute this action. Instead, use ResponseToUserAction with message_type='clarification' to ask the user for the song name."
    )
    immediate_response: bool = Field(
        description=
        "Should always be True for get_music_structure as it's a retrieval action that doesn't need user input",
        default=True)


class ResponseToUserParams(BaseModel):
    message: str = Field(description="The message to send to the user")
    requires_response: bool = Field(
        description="Whether this message requires a response from the user",
        default=False)
    message_type: str = Field(
        description=
        "The type of message being sent to the user. If the user asks you to perform an action (e.g. generate an animation), execute it directly without informing the user. If the user asks a question, provide your answer here.",
        enum=["clarification", "answer"],
        default="information")
    immediate_response: bool = Field(
        description=
        "Should always be False for response_to_user when message_type is 'clarification' or 'question', or when requires_response is True. For information messages that don't require response, can be True.",
        default=False)


# Action models with specific parameter types
class UpdateAnimationAction(BaseModel, Generic[T]):
    name: Literal["update_animation"]
    params: UpdateAnimationParams[T]


class GetAnimationAction(BaseModel):
    name: Literal["get_animation"]
    params: GetAnimationParams


class GetMemoryAction(BaseModel):
    name: Literal["get_memory"]
    params: GetMemoryParams


class GetMusicStructureAction(BaseModel):
    name: Literal["get_music_structure"]
    params: GetMusicStructureParams


class ResponseToUserAction(BaseModel):
    name: Literal["response_to_user"]
    params: ResponseToUserParams


# Union type for all possible actions
ActionType: TypeAlias = Annotated[Union[UpdateAnimationAction[T],
                                        GetAnimationAction, GetMemoryAction,
                                        GetMusicStructureAction,
                                        ResponseToUserAction],
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
        "A brief explanation of the reasoning behind the chosen action and the overall plan. High level plan of the animation journey. Be concise and to the point."
    )
    actions_plan: str = Field(
        description=
        "Write in natural language the planned actions, in bullet points, to be executed in sequence in future turns. This plan can be revised in subsequent turns. Only mention which actions and with what order. No need to explain why. You explain why in the reasoning field.",
        default="")
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
