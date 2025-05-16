from pydantic import BaseModel, Field
from typing import List, Literal, Union, Optional, Dict, Any, Annotated, TypeVar, Generic
from typing_extensions import TypeAlias
from pydantic import root_validator


# Action parameter models
class UpdateAnimationParams(BaseModel):
    animation_sequence: Any = Field(
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
class UpdateAnimationAction(BaseModel):
    name: Literal["update_animation"]
    params: UpdateAnimationParams


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
ActionType: TypeAlias = Annotated[Union[UpdateAnimationAction,
                                        GetAnimationAction, GetMemoryAction,
                                        GetMusicStructureAction,
                                        ResponseToUserAction],
                                  Field(discriminator='name')]

# Generic type for framework-specific animation schema
T = TypeVar('T', bound=BaseModel)


class MainSchema(BaseModel, Generic[T]):
    """
    Main schema that combines action handling with framework-specific animation schemas.
    The generic type T represents the framework-specific animation schema.
    """
    reasoning: str = Field(
        description=
        "A brief explanation of the reasoning behind the chosen actions. Make sure to specify which actions were chosen and why."
    )
    actions: List[ActionType] = Field(
        description="List of actions to be executed in sequence",
        default_factory=list)
    user_instruction: str = Field(
        description=
        "The instruction that was given to the model to generate this response."
    )
    animation_data: Optional[BaseModel] = Field(
        default=None,
        description=
        "Framework-specific animation data that will be validated against the framework's schema"
    )

    # def validate_action_params(
    #         self, action: ActionType) -> Optional[ResponseToUserAction]:
    #     """
    #     Validates the parameters of an action and returns a ResponseToUserAction if parameters are missing.
    #     Returns None if all required parameters are present.
    #     """
    #     if action.name == "get_animation":
    #         if action.params.step_number < 0:
    #             return ResponseToUserAction(
    #                 name="response_to_user",
    #                 params=ResponseToUserParams(
    #                     message="Please provide a valid step number (>= 0)",
    #                     message_type="clarification",
    #                     requires_response=True,
    #                     immediate_response=False))
    #     elif action.name == "get_music_structure":
    #         if not action.params.song_name:
    #             return ResponseToUserAction(
    #                 name="response_to_user",
    #                 params=ResponseToUserParams(
    #                     message="Please provide the song name",
    #                     message_type="clarification",
    #                     requires_response=True,
    #                     immediate_response=False))
    #     return None

    # @root_validator(pre=True)
    # def validate_actions(cls, values: Dict[str, Any]) -> Dict[str, Any]:
    #     """
    #     Validates all actions and replaces any action with missing parameters with a ResponseToUserAction.
    #     """
    #     if "actions" in values:
    #         validated_actions = []
    #         for action in values["actions"]:
    #             if isinstance(action, dict):
    #                 action = ActionType.parse_obj(action)
    #             clarification = cls.validate_action_params(action)
    #             if clarification:
    #                 validated_actions.append(clarification)
    #             else:
    #                 validated_actions.append(action)
    #         values["actions"] = validated_actions
    #     return values

    @classmethod
    def with_framework_schema(
            cls, framework_schema: type[BaseModel]) -> type['MainSchema']:
        """
        Creates a new MainSchema class with the framework's schema as the animation_data type.
        This ensures proper validation of the animation data against the framework's schema.
        """

        class FrameworkMainSchema(cls):
            animation_data: Optional[framework_schema] = Field(
                default=None,
                description=
                f"Animation data validated against {framework_schema.__name__}"
            )

        return FrameworkMainSchema
