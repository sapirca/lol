from pydantic import BaseModel, Field, validator, ValidationError
from typing import List, Literal, Union, Optional, Dict, Any, Annotated, TypeVar, Generic
from typing_extensions import TypeAlias
import json  # Import the json module
import re  # Import regex module
from enum import Enum

# Generic type for framework-specific animation schema
T = TypeVar('T', bound=BaseModel)


class ConfirmationType(str, Enum):
    ASK_EVERY_TIME = "ask-every-time"
    AUTO_RUN = "auto-run"
    NO_ACTION_REQUIRED = "no-action-required"


class TurnType(str, Enum):
    LLM = "llm"
    USER = "user"


class BaseActionParams(BaseModel):
    confirmation_type: ConfirmationType = Field(
        description=
        "How this action should be handled regarding user confirmation. "
        "ask-every-time: Always ask for confirmation, "
        "auto-run: Run automatically but still refresh UI, "
        "no-action-required: No confirmation needed (for informational actions)"
    )
    turn: TurnType = Field(
        description="Whose turn is it to act next - LLM or USER",
        default=TurnType.USER)

    @validator('confirmation_type', pre=True)
    def convert_confirmation_type(cls, v):
        if isinstance(v, str):
            try:
                return ConfirmationType(v)
            except ValueError:
                raise ValueError(
                    f"Invalid confirmation type: {v}. Must be one of {[e.value for e in ConfirmationType]}"
                )
        return v

    @validator('turn', pre=True)
    def convert_turn(cls, v):
        if isinstance(v, str):
            try:
                return TurnType(v)
            except ValueError:
                raise ValueError(
                    f"Invalid turn type: {v}. Must be one of {[e.value for e in TurnType]}"
                )
        return v

    class Config:
        use_enum_values = True


# Action parameter models
class UpdateAnimationParams(BaseActionParams, Generic[T]):
    confirmation_type: ConfirmationType = ConfirmationType.NO_ACTION_REQUIRED
    turn: TurnType = TurnType.USER
    animation_sequence: T = Field(
        description=
        "The animation data to be processed - will be validated against framework-specific schema."
    )


class GetAnimationParams(BaseActionParams):
    confirmation_type: ConfirmationType = ConfirmationType.AUTO_RUN
    turn: TurnType = TurnType.LLM
    step_number: int = Field(
        description=
        "The step number of the animation to retrieve. If this parameter is missing, unknown to you or invalid (< 0), do not execute this action. Instead, use AskUserAction to ask the user for a valid step number.",
        ge=0)


# class InformUserParams(BaseModel):
#     message: str = Field(description="The message to send to the user")
#     message_type: Literal["information", "answer", "error"] = Field(
#         description=
#         "The type of message being sent. Use 'information' for general info and success messages, 'answer' for answers to user questions, 'error' for error messages.",
#         default="information")
#     immediate_response: Literal[False] = Field(
#         description=
#         "Always False for inform_user as it's a one-way communication")


class QuestionParams(BaseActionParams):
    confirmation_type: ConfirmationType = ConfirmationType.NO_ACTION_REQUIRED
    turn: TurnType = TurnType.USER
    message: str = Field(
        description="The question or clarification request for the user")
    is_clarification: bool = Field(
        description=
        "Whether this is a clarification request (True) or a new question (False)",
        default=False)


class AnswerUserParams(BaseActionParams):
    confirmation_type: ConfirmationType = ConfirmationType.NO_ACTION_REQUIRED
    turn: TurnType = TurnType.USER
    message: str = Field(description="The answer to the user's question")


class GenerateBeatBasedEffectParams(BaseActionParams):
    """
    This action generates the data for the BrightnessEffectConfig. The brightness effect is synchronized to the beat, also taking into account the time frame that is specified by the start_time_ms and end_time_ms parameters.
    This data can be put into the animation for any element you want, make sure to put this alongside a coloring like const_color or rainbow.
    """
    confirmation_type: ConfirmationType = ConfirmationType.ASK_EVERY_TIME
    turn: TurnType = TurnType.USER
    beat_based_effect_type: Literal[
        "breath", "soft_pulse", "strobe", "fade_in_out", "blink",
        "blink_and_fade_out", "fade_in_and_disappear"] = Field(
            description="The type of beat-based effect to retrieve")
    start_time_ms: int = Field(
        description="The start time in milliseconds for the effect", ge=0)
    end_time_ms: int = Field(
        description="The end time in milliseconds for the effect", ge=0)
    bpm: int = Field(description="The beats per minute of the song", gt=0)


class MemorySuggestionParams(BaseActionParams):
    confirmation_type: ConfirmationType = ConfirmationType.NO_ACTION_REQUIRED
    turn: TurnType = TurnType.USER
    message: str = Field(description="The memory suggestion for the user")


class AddToMemoryParams(BaseActionParams):
    confirmation_type: ConfirmationType = ConfirmationType.ASK_EVERY_TIME
    turn: TurnType = TurnType.USER
    key: str = Field(
        description="The key under which to store the memory value")
    value: str = Field(description="The value to store in memory")


class RemoveMemoryParams(BaseActionParams):
    confirmation_type: ConfirmationType = ConfirmationType.ASK_EVERY_TIME
    turn: TurnType = TurnType.USER
    key: str = Field(description="The key of the memory entry to remove")


class UpdateMemoryParams(BaseActionParams):
    confirmation_type: ConfirmationType = ConfirmationType.ASK_EVERY_TIME
    turn: TurnType = TurnType.USER
    key: str = Field(description="The key of the memory entry to update")
    value: str = Field(description="The new value to set or append")


class GetMusicStructureParams(BaseActionParams):
    confirmation_type: ConfirmationType = ConfirmationType.ASK_EVERY_TIME
    turn: TurnType = TurnType.LLM
    structure_type: Literal[
        "lyrics", "key_points", "drum_pattern",
        "beats"] = Field(description="The type of music structure to retrieve")
    song_name: str = Field(
        description="The name of the song to get the structure for")


class SaveCompoundEffectParams(BaseActionParams):
    confirmation_type: ConfirmationType = ConfirmationType.ASK_EVERY_TIME
    turn: TurnType = TurnType.USER
    name: str = Field(description="The name of the compound effect to save")
    effects: List[Any] = Field(
        description=
        "The list of EffectProto objects that make up the compound effect")
    tags: List[str] = Field(
        description="The tags to associate with this compound effect")


class GetCompoundEffectParams(BaseActionParams):
    confirmation_type: ConfirmationType = ConfirmationType.ASK_EVERY_TIME
    turn: TurnType = TurnType.USER
    name: str = Field(
        description="The name of the compound effect to retrieve")


class GetCompoundEffectsKeysAndTagsParams(BaseActionParams):
    confirmation_type: ConfirmationType = ConfirmationType.ASK_EVERY_TIME
    turn: TurnType = TurnType.USER


# // Random effects
class GetRandomEffectParams(BaseActionParams):
    confirmation_type: ConfirmationType = ConfirmationType.ASK_EVERY_TIME
    turn: TurnType = TurnType.USER
    number: int = Field(
        description="The number of the random effect to retrieve", ge=0)


class DeleteRandomEffectParams(BaseActionParams):
    confirmation_type: ConfirmationType = ConfirmationType.ASK_EVERY_TIME
    turn: TurnType = TurnType.LLM
    number: int = Field(
        description="The number of the random effect to delete", ge=0)


# Action models with specific parameter types
class UpdateAnimationAction(BaseModel, Generic[T]):
    name: Literal["update_animation"]
    params: UpdateAnimationParams[T]


# Animation Actions
class GetAnimationAction(BaseModel):
    name: Literal["get_animation"]
    params: GetAnimationParams


# General Actions
class AnswerUserAction(BaseModel):
    name: Literal["answer_user"]
    params: AnswerUserParams


class QuestionAction(BaseModel):
    name: Literal["question"]
    params: QuestionParams


#  Memory Actions
class AddToMemoryAction(BaseModel):
    name: Literal["add_to_memory"]
    params: AddToMemoryParams


class RemoveMemoryAction(BaseModel):
    name: Literal["remove_memory"]
    params: RemoveMemoryParams


class UpdateMemoryAction(BaseModel):
    name: Literal["update_memory"]
    params: UpdateMemoryParams


class MemorySuggestionAction(BaseModel):
    name: Literal["memory_suggestion"]
    params: MemorySuggestionParams


# // Music Retrieval (by type: lyrics, key-points, beats…)
class GetMusicStructureAction(BaseModel):
    name: Literal["get_music_structure"]
    params: GetMusicStructureParams


# // Abstract Animation
class GenerateBeatBasedEffectAction(BaseModel):
    name: Literal["generate_beat_based_effect"]
    params: GenerateBeatBasedEffectParams


# // Compound Effects


class SaveCompoundEffectAction(BaseModel):
    name: Literal["save_compound_effect"]
    params: SaveCompoundEffectParams


class GetCompoundEffectAction(BaseModel):
    name: Literal["get_compound_effect"]
    params: GetCompoundEffectParams


class GetCompoundEffectsKeysAndTagsAction(BaseModel):
    name: Literal["get_compound_effects_keys_and_tags"]
    params: GetCompoundEffectsKeysAndTagsParams


# Action models with specific parameter types
class GetRandomEffectAction(BaseModel):
    name: Literal["get_random_effect"]
    params: GetRandomEffectParams


class DeleteRandomEffectAction(BaseModel):
    name: Literal["delete_random_effect"]
    params: DeleteRandomEffectParams


# Union type for all possible actions
ActionType: TypeAlias = Annotated[Union[UpdateAnimationAction[T],
                                        GetAnimationAction, AddToMemoryAction,
                                        QuestionAction, MemorySuggestionAction,
                                        AnswerUserAction,
                                        GenerateBeatBasedEffectAction,
                                        RemoveMemoryAction, UpdateMemoryAction,
                                        GetMusicStructureAction,
                                        SaveCompoundEffectAction,
                                        GetCompoundEffectAction,
                                        GetCompoundEffectsKeysAndTagsAction,
                                        GetRandomEffectAction,
                                        DeleteRandomEffectAction],
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
        "If a string is provided, it will be parsed as JSON. "
        "IMPORTANT: Do NOT include any XML-like tags (e.g., <invoke>, </invoke>) in the response. "
        "The response should be pure JSON only.")

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
