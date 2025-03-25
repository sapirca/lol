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

# class ConstValueFloatFunctionConfig(BaseModel):
#     value: float = Field(default=0.0, description="Constant float value.")

# class LinearFloatFunctionConfig(BaseModel):
#     start: float = Field(default=0.0, description="Starting float value.")
#     end: float = Field(default=0.0, description="Ending float value.")

# class SinFloatFunctionConfig(BaseModel):
#     min: float = Field(default=0.0, description="Minimum float value.")
#     max: float = Field(default=0.0, description="Maximum float value.")
#     phase: float = Field(default=0.0,
#                          description="Phase offset of the sine wave.")
#     repeats: float = Field(
#         default=0.0, description="Number of repetitions of the sine wave.")

# class StepsFloatFunctionConfig(BaseModel):
#     num_steps: float = Field(default=0.0,
#                              description="Number of steps in the function.")
#     diff_per_step: float = Field(default=0.0,
#                                  description="Difference between each step.")
#     first_step_value: float = Field(default=0.0,
#                                     description="Value of the first step.")

# class HalfFloatFunctionConfig(BaseModel):
#     f1: "FloatFunction" = Field(default_factory=lambda: FloatFunction(),
#                                 description="First half function.")
#     f2: "FloatFunction" = Field(default_factory=lambda: FloatFunction(),
#                                 description="Second half function.")

# class Comb2FloatFunctionConfig(BaseModel):
#     f1: "FloatFunction" = Field(default_factory=lambda: FloatFunction(),
#                                 description="First function to combine.")
#     amount1: float = Field(default=0.0,
#                            description="Amount of the first function.")
#     f2: "FloatFunction" = Field(default_factory=lambda: FloatFunction(),
#                                 description="Second function to combine.")
#     amount2: float = Field(default=0.0,
#                            description="Amount of the second function.")

# class FloatFunction(BaseModel):
#     _one_of_dict = {
#         "FloatFunction.function": {
#             "fields": {
#                 "comb2", "const_value", "half", "linear", "repeat", "sin",
#                 "steps"
#             }
#         }
#     }
#     one_of_validator = model_validator(mode="before")(check_one_of)
#     const_value: ConstValueFloatFunctionConfig = Field(
#         description="Constant float function.")
#     linear: LinearFloatFunctionConfig = Field(
#         description="Linear float function.")
#     sin: SinFloatFunctionConfig = Field(
#         description="Sine wave float function.")
#     steps: StepsFloatFunctionConfig = Field(
#         description="Steps float function.")
#     repeat: "RepeatFloatFunctionConfig" = Field(
#         description="Repeat float function.")
#     half: HalfFloatFunctionConfig = Field(description="Half float function.")
#     comb2: Comb2FloatFunctionConfig = Field(
#         description="Combine 2 float functions.")

# class RepeatFloatFunctionConfig(BaseModel):
#     numberOfTimes: float = Field(
#         default=0.0, description="Number of times to repeat the function.")
#     funcToRepeat: FloatFunction = Field(description="Function to repeat.")


class HSV(BaseModel):
    hue: float = Field(default=0.0, description="Hue value.")
    sat: float = Field(default=0.0, description="Saturation value.")
    val: float = Field(default=0.0, description="Value (brightness) value.")


class ConstColorEffectConfig(BaseModel):
    color: HSV = Field(default_factory=HSV, description="Constant HSV color.")


class RainbowEffectConfig(BaseModel):
    """
     message RainbowEffectConfig {
     float hue_start = 1; // p2p: {"description": "Starting hue function for the rainbow."}
     float hue_end = 2;   // p2p: {"description": "Ending hue function for the rainbow."}
 }
    """

    hue_start: float = Field(
        default=0.0, description="Starting hue function for the rainbow.")
    hue_end: float = Field(default=0.0,
                           description="Ending hue function for the rainbow.")


class BrightnessEffectConfig(BaseModel):
    mult_factor: float = Field(description="Multiplier factor for brightness.")


class HueEffectConfig(BaseModel):
    offset_factor: float = Field(description="Offset factor for hue.")


class SaturationEffectConfig(BaseModel):
    mult_factor: float = Field(description="Multiplier factor for saturation.")


class SnakeEffectConfig(BaseModel):
    head: float = Field(description="Head position function for the snake.")
    tail_length: float = Field(
        description="Tail length function for the snake.")
    cyclic: bool = Field(default=False,
                         description="Whether the snake is cyclic.")


class SegmentEffectConfig(BaseModel):
    start: float = Field(description="Segment start position function.")
    end: float = Field(description="Segment end position function.")


class GlitterEffectConfig(BaseModel):
    intensity: float = Field(description="Glitter intensity function.")
    sat_mult_factor: float = Field(
        description="Saturation multiplier factor for glitter.")


class AlternateEffectConfig(BaseModel):
    numberOfPixels: int = Field(
        default=0, description="Number of pixels for the alternate effect.")
    hue_offset: float = Field(
        description="Hue offset function for the alternate effect.")
    sat_mult: float = Field(
        description="Saturation multiplier function for the alternate effect.")
    brightness_mult: float = Field(
        description="Brightness multiplier function for the alternate effect.")


class EffectConfig(BaseModel):
    start_time: int = Field(
        default=0, description="Start time of the effect in milliseconds.")
    end_time: int = Field(
        default=0, description="End time of the effect in milliseconds.")
    segments: str = Field(default="",
                          description="Segments to apply the effect to.")
    repeat_num: float = Field(
        default=0.0, description="Number of times to repeat the effect.")
    repeat_start: float = Field(default=0.0,
                                description="Start time of the repeat.")
    repeat_end: float = Field(default=0.0,
                              description="End time of the repeat.")


# >>>>>>>>>>>>>>>>>>>>>>>>
class EffectProto(BaseModel):
    effect_config: EffectConfig = Field(
        default_factory=EffectConfig,
        description="General configuration for the effect.")
    const_color: typing.Optional[ConstColorEffectConfig] = Field(
        description="The LEDs will display a single, constant color.")
    rainbow: typing.Optional[RainbowEffectConfig] = Field(
        description=
        "The LEDs will cycle through a spectrum of colors, creating a rainbow effect."
    )
    brightness: typing.Optional[BrightnessEffectConfig] = Field(
        description="Adjusts the overall brightness of the LEDs.")
    hue: typing.Optional[HueEffectConfig] = Field(
        description="Cycles through different hues (colors) on the LEDs.")
    saturation: typing.Optional[SaturationEffectConfig] = Field(
        description=
        "Adjusts the purity of the colors displayed on the LEDs. Below 0.8 is less saturated, pastel appearance."
    )
    snake: typing.Optional[SnakeEffectConfig] = Field(
        description=
        "A segment of lit LEDs will move along the strip, resembling a snake.")
    segment: typing.Optional[SegmentEffectConfig] = Field(
        description=
        "Applies an effect to a specific segment of LEDs, identified by its ID."
    )
    glitter: typing.Optional[GlitterEffectConfig] = Field(
        description=
        "Randomly lights up individual LEDs in a specified color, creating a glittery appearance."
    )
    alternate: typing.Optional[AlternateEffectConfig] = Field(
        description=
        "The LEDs will alternate between two specified colors at a defined period."
    )

    # @model_validator(mode="after")
    # def check_one_of_effect(self):
    #     effects_set = sum(1 for effect in [self.const_color, self.rainbow]
    #                       if effect is not None)
    #     if effects_set != 1:
    #         raise ValueError(
    #             "Exactly one of const_color or rainbow must be set.")
    #     return self

    @model_validator(mode="after")
    def check_one_of_effect(self):
        effects = [
            self.const_color,
            self.rainbow,
            self.brightness,
            self.hue,
            self.saturation,
            self.snake,
            self.segment,
            self.glitter,
            self.alternate,
        ]
        effects_set = sum(1 for effect in effects if effect is not None)
        if effects_set != 1:
            raise ValueError("Exactly one effect type must be set.")
        return self


# class ElementsEffectProto(BaseModel):
#     elements: typing.List[str] = Field(
#         default_factory=list,
#         description=
#         "List of elements to be animated. Each element name is a string.")
#     effects: typing.List[EffectProto] = Field(
#         default_factory=list,
#         description="List of effects to be animated on the given elements list."
#     )


class AnimationProto(BaseModel):
    """
     TODO sapir how to split it per element?
    """

    effects: typing.List[EffectProto] = Field(
        default_factory=list, description="List of effects in the animation.")
    duration_ms: int = Field(
        default=0,
        description="Duration of the entire animation in milliseconds.")
    num_repeats: int = Field(
        default=0,
        description="Number of times to repeat the animation (0 means forever)."
    )


class KivseeSchema(BaseModel):
    """
    Represents the full animation response, with the song name and reasoning.
    """

    instruction: str = Field(
        default="",
        description=
        "The user instruction that the was given to the model to generate this animation response."
    )
    reasoning: str = Field(
        default="",
        description=
        "A brief explanation of the reasoning behind the animation, or why these changes in the animation were made."
    )
    animation: AnimationProto = Field(default_factory=AnimationProto,
                                      description="The whole animation.")
    name: str = Field(default="", description="The animation title.")
