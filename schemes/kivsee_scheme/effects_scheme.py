# This is an automatically generated file, please do not change
# gen by protobuf_to_pydantic[v0.3.1.1](https://github.com/so1n/protobuf_to_pydantic)
# Protobuf Version: 4.25.6
# Pydantic Version: 2.10.6
from google.protobuf.message import Message  # type: ignore
from protobuf_to_pydantic.customer_validator import check_one_of
from pydantic import BaseModel
from pydantic import Field
from pydantic import model_validator
import typing


class AbstractFloatFunctionConfig(BaseModel):
    pass


class ConstValueFloatFunctionConfig(BaseModel):
    value: float = Field(..., description="Constant float value.")


class LinearFloatFunctionConfig(BaseModel):
    start: float = Field(..., description="Starting float value.")
    end: float = Field(..., description="Ending float value.")


class SinFloatFunctionConfig(BaseModel):
    min: float = Field(..., description="Minimum float value.")
    max: float = Field(..., description="Maximum float value.")
    phase: float = Field(..., description="Phase offset of the sine wave.")
    repeats: float = Field(
        ..., description="Number of repetitions of the sine wave.")


class StepsFloatFunctionConfig(BaseModel):
    num_steps: float = Field(description="Number of steps in the function.")
    diff_per_step: float = Field(description="Difference between each step.")
    first_step_value: float = Field(description="Value of the first step.")


# class RepeatFloatFunctionConfig(BaseModel):
#     numberOfTimes: float = Field(
#         description="Number of times to repeat the function.")
#     funcToRepeat: FloatFunction = Field(description="Function to repeat.")

# class HalfFloatFunctionConfig(BaseModel):
#     f1: "FloatFunction" = Field(default_factory=lambda: FloatFunction(),
#                                 description="First half function.")
#     f2: "FloatFunction" = Field(default_factory=lambda: FloatFunction(),
#                                 description="Second half function.")

# class Comb2FloatFunctionConfig(BaseModel):
#     f1: "FloatFunction" = Field(default_factory=lambda: FloatFunction(),
#                                 description="First function to combine.")
#     amount1: float = Field(description="Amount of the first function.")
#     f2: "FloatFunction" = Field(default_factory=lambda: FloatFunction(),
#                                 description="Second function to combine.")
#     amount2: float = Field(description="Amount of the second function.")


class FloatFunction(BaseModel):
    const_value: typing.Optional[ConstValueFloatFunctionConfig] = Field(
        default=None, description="Constant float function.")
    linear: typing.Optional[LinearFloatFunctionConfig] = Field(
        default=None, description="Linear float function.")
    sin: typing.Optional[SinFloatFunctionConfig] = Field(
        default=None, description="Sine wave float function.")
    steps: typing.Optional[StepsFloatFunctionConfig] = Field(
        default=None, description="Steps float function.")
    # repeat: typing.Optional[RepeatFloatFunctionConfig] = Field(
    #     description="Repeat float function.")
    # half: typing.Optional[HalfFloatFunctionConfig] = Field(
    #     description="Half float function.")
    # comb2: typing.Optional[Comb2FloatFunctionConfig] = Field(
    #     description="Combine 2 float functions.")

    @model_validator(mode="after")
    def check_one_of_effect(self):
        effects = [
            self.const_value,
            self.linear,
            self.sin,
            self.steps,
            # self.repeat,
            # self.half,
            # self.comb2,
        ]
        effects_set = sum(1 for effect in effects if effect is not None)
        if effects_set != 1:
            raise ValueError(f"all effects are {effects}.")
        return self


class HSV(BaseModel):
    hue: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description=
        "Hue value between 0.0 to 1.0. Where 0.0 is red, 0.33 is green, 0.67 is blue, and 1.0 is red."
    )
    sat: float = Field(default=1.0,
                       ge=0.0,
                       le=1.0,
                       description="Saturation value between 0.0 and 1.0.")
    val: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Value (brightness) value between 0.0 and 1.0.")


class ConstColorEffectConfig(BaseModel):
    color: HSV = Field(default_factory=HSV, description="Constant HSV color.")


class RainbowEffectConfig(BaseModel):
    hue_start: FloatFunction = Field(
        ..., description="Starting hue function for the rainbow.")
    hue_end: FloatFunction = Field(
        ..., description="Ending hue function for the rainbow.")


class BrightnessEffectConfig(BaseModel):
    mult_factor: FloatFunction = Field(
        ..., description="Multiplier factor for brightness.")


class HueEffectConfig(BaseModel):
    offset_factor: FloatFunction = Field(...,
                                         description="Offset factor for hue.")


class SaturationEffectConfig(BaseModel):
    mult_factor: FloatFunction = Field(
        ..., description="Multiplier factor for saturation.")


class SnakeEffectConfig(BaseModel):
    head: FloatFunction = Field(
        ..., description="Head position function for the snake.")
    tail_length: FloatFunction = Field(
        ..., description="Tail length function for the snake.")
    cyclic: bool = Field(default=False,
                         description="Whether the snake is cyclic.")


# class SegmentEffectConfig(BaseModel):
#     start: FloatFunction = Field(
#         ..., description="Segment start position function.")
#     end: FloatFunction = Field(...,
#                                description="Segment end position function.")

# class GlitterEffectConfig(BaseModel):
#     intensity: FloatFunction = Field(...,
#                                      description="Glitter intensity function.")
#     sat_mult_factor: FloatFunction = Field(
#         ..., description="Saturation multiplier factor for glitter.")

# class AlternateEffectConfig(BaseModel):
#     numberOfPixels: int = Field(
#         ..., description="Number of pixels for the alternate effect.")
#     hue_offset: FloatFunction = Field(
#         ..., description="Hue offset function for the alternate effect.")
#     sat_mult: FloatFunction = Field(
#         ...,
#         description="Saturation multiplier function for the alternate effect.")
#     brightness_mult: FloatFunction = Field(
#         ...,
#         description="Brightness multiplier function for the alternate effect.")


class EffectConfig(BaseModel):
    start_time: int = Field(
        ...,
        description=
        "Start time of the effect in milliseconds. Extract from the list of bars you provided in the prompt."
    )
    end_time: int = Field(
        ...,
        description=
        "End time of the effect in milliseconds. The end of a bar is the begining of the next bar, use the miliseconds from the list of bars you provided in the prompt."
    )
    segments: str = Field(
        ...,
        description=
        "Specifies the segments of LEDs to which the effect will be applied. This allows targeting specific subsets of LEDs for more variety in the animation. For example, 'b1' might represent every 4th LED. The default segment is 'all', which means the effect will apply to all LEDs of the element.",
        enum=["centric", "updown", "arc", "ind", "b1", "b2", "rand", "all"])
    # repeat_num: float = Field(
    #     description="Number of times to repeat the effect.")
    # repeat_start: float = Field(description="Start time of the repeat.")
    # repeat_end: float = Field(
    #     description=
    #     "End time of the repeat. number bewteen 0-1. where 1 is 100% of this time, end_time, and zero is the begining of start_time."
    # )


# >>>>>>>>>>>>>>>>>>>>>>>>
class EffectProto(BaseModel):
    """
    Represents a single effect in the animation sequence.
    IMPORTANT: Each effect configuration must have EXACTLY ONE color effect type set (const_color or rainbow).
    Other effects (brightness, hue, etc.) are optional and can be combined.
    """

    effect_number: int = Field(
        ...,
        description=
        "The position of the effect in the animation sequence, starting from 1. This is used to reference the effect if needed. For example, the first effect is 1, the second is 2, and so on. The user can specify the effect number in the request, and this field will help identify the corresponding effect."
    )
    title: str = Field(
        default="",
        description=
        "A title for the effect. This is used to identify the effect and can be used for grouping similar effects together."
    )
    beat_and_bar: str = Field(
        ...,
        description=
        "if relevant, write the beat and bar this effect is applied to. e.g., 'Bar 2: 11th beat'."
    )

    elements: typing.List[typing.Literal[
        "ring7", "ring8", "ring9", "ring10", "ring11", "ring12"]] = Field(
            default_factory=list,
            min_length=1,
            description=
            "Specifies the list of elements (rings) to which this effect applies. The art installation consists of six sequentially arranged rings, numbered 7 through 12, categorized based on their arrangement and characteristics. Categories include all rings, odd/even rings, left/right sides, center rings, and outer rings. For example, odd rings [ring7, ring9, ring11], even rings [ring8, ring10, ring12], or outer rings [ring7, ring8, ring11, ring12]. This allows for creating diverse animations by targeting specific rings or combinations. For example, you can animate rings sequentially, alternate between left and right, or create patterns that move across the rings for more dynamic effects. In your response, list all the rings you want to animate."
        )
    effect_config: EffectConfig = Field(
        default_factory=EffectConfig,
        description="General configuration for the effect.")

    const_color: typing.Optional[ConstColorEffectConfig] = Field(
        default=None,
        description=
        "[IMPORTANT: Exactly one of const_color or rainbow must be set] The LEDs will display a single, constant color."
    )
    rainbow: typing.Optional[RainbowEffectConfig] = Field(
        default=None,
        description=
        "[IMPORTANT: Exactly one of const_color or rainbow must be set] The LEDs will cycle through a spectrum of colors, creating a rainbow effect."
    )
    brightness: typing.Optional[BrightnessEffectConfig] = Field(
        default=None,
        description="Adjusts the overall brightness of the LEDs.")
    hue: typing.Optional[HueEffectConfig] = Field(
        default=None,
        description="Cycles through different hues (colors) on the LEDs.")
    saturation: typing.Optional[SaturationEffectConfig] = Field(
        default=None,
        description=
        "Adjusts the purity of the colors displayed on the LEDs. Below 0.8 is less saturated, pastel appearance."
    )
    snake: typing.Optional[SnakeEffectConfig] = Field(
        default=None,
        description=
        "A segment of lit LEDs will move along the strip, resembling a snake.")
    # segment: typing.Optional[SegmentEffectConfig] = Field(
    #     default=None,
    #     description=
    #     "Applies an effect to a specific segment of LEDs, identified by its ID."
    # )
    # glitter: typing.Optional[GlitterEffectConfig] = Field(
    #     default=None,
    #     description=
    #     "Randomly lights up individual LEDs in a specified color, creating a glittery appearance."
    # )
    # alternate: typing.Optional[AlternateEffectConfig] = Field(
    #     default=None,
    #     description=
    #     "The LEDs will alternate between two specified colors at a defined period."
    # )

    effect_summary: str = Field(
        default="",
        description=
        "A brief summary of what this effect does. Focus on which colors the user see and which patterns and motions (e.g. rapid blinking pink snake, with green b1 segment). Provides a visual overview so that the user can understand which one is it.."
    )

    @model_validator(mode="after")
    def check_one_of_effect(self):
        # Check that exactly one color effect is set
        color_effects = [self.const_color, self.rainbow]
        color_effects_set = sum(1 for effect in color_effects
                                if effect is not None)
        if color_effects_set != 1:
            raise ValueError(
                f"Exactly one color effect (const_color or rainbow) must be set. Found {color_effects_set} color effects: {[e.__class__.__name__ for e in color_effects if e is not None]}"
            )
        return self


class AnimationProto(BaseModel):
    effects: typing.List[EffectProto] = Field(
        default_factory=list, description="List of effects in the animation.")
    duration_ms: int = Field(
        default=0,
        description=
        "Duration of the entire song in milliseconds. Even if the animation does not last the entire song, this value should be the same as the song duration."
    )
    num_repeats: int = Field(
        default=1,
        description=
        "Number of times to repeat the animation (0 means forever). Usually, this should be 1, but if the user specifies a repeat count in the prompt, you should put it here. If the user does not specify a repeat count, you should put 1 here. If the user specifies a repeat count of 0, it means forever."
    )


class KivseeSchema(BaseModel):
    """
    Represents the full animation response, with the song name and reasoning.
    """

    # instruction: str = Field(
    #     default="",
    #     description=
    #     "The user instruction that the was given to the model to generate this animation response."
    # )
    # reasoning: str = Field(
    #     default="",
    #     description=
    #     "A brief explanation of the reasoning behind the animation, or why these changes in the animation were made."
    # )
    animation: AnimationProto = Field(default_factory=AnimationProto,
                                      description="The whole animation.")
    name: str = Field(
        default="",
        description=
        ("The animation title. If the user specifies the song name as 'some_name', "
         "you should put 'some_name' here. The name must not contain spaces or special characters; "
         "it should only include letters, numbers, and underscores (_)."))
