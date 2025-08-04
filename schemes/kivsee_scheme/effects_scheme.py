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
# from typing import Literal, List, Optional, Type
import copy

# Base template for float function configurations - now empty as per your instruction
class FloatFunctionTemplate(BaseModel):
    """Base template for all float function configurations (now empty)"""
    pass


# Basic float function configurations (no start_time/end_time here, they are in FloatFunction)
class ConstValueFloatFunctionConfig(FloatFunctionTemplate):
    """Constant value function configuration"""
    value: float = Field(..., description="Constant float value")


class LinearFloatFunctionConfig(FloatFunctionTemplate):
    """Linear function configuration"""
    start: float = Field(..., description="Starting float value")
    end: float = Field(..., description="Ending float value")


class SinFloatFunctionConfig(FloatFunctionTemplate):
    """Sine wave function configuration"""
    min: float = Field(..., description="Minimum float value")
    max: float = Field(..., description="Maximum float value")
    phase: float = Field(..., description="Phase offset of the sine wave")
    repeats: float = Field(
        ..., description="Number of repetitions of the sine wave")


class StepsFloatFunctionConfig(FloatFunctionTemplate):
    """Creates a step function that changes value at regular intervals.
    The function starts at first_step_value and changes by diff_per_step at each step,
    creating a sequence of constant values over the specified number of steps."""
    first_step_value: float = Field(
        description="The starting value of the step function")
    diff_per_step: float = Field(
        description=
        "The change in value between consecutive steps. For example, 0.5 means each step increases by 0.5, while -0.5 means each step decreases by 0.5"
    )
    num_steps: float = Field(
        description=
        "The total number of constant-value segments in the function. For example, with 6 steps over 3 seconds, each step will last 0.5 seconds and change by diff_per_step"
    )


# Main FloatFunction class that can contain any of the above configurations
# It no longer holds start_time and end_time
class FloatFunction(BaseModel):  # Changed to inherit directly from BaseModel
    """Main class for float functions that can contain any configuration type"""
    # Removed start_time and end_time from here

    const_value: typing.Optional[ConstValueFloatFunctionConfig] = Field(
        default=None, description="Constant float function")
    linear: typing.Optional[LinearFloatFunctionConfig] = Field(
        default=None, description="Linear float function")
    sin: typing.Optional[SinFloatFunctionConfig] = Field(
        default=None, description="Sine wave float function")
    steps: typing.Optional[StepsFloatFunctionConfig] = Field(
        default=None, description="Steps float function")
    # Using string literals for forward references
    repeat: typing.Optional['RepeatFloatFunctionConfig'] = Field(
        default=None, description="Repeat float function")
    half: typing.Optional['HalfFloatFunctionConfig'] = Field(
        default=None, description="Half float function")
    comb2: typing.Optional['Comb2FloatFunctionConfig'] = Field(
        default=None, description="Combine 2 float functions")

    @model_validator(mode="after")
    def check_one_of_effect(self):
        effects = [
            self.const_value,
            self.linear,
            self.sin,
            self.steps,
            self.repeat,
            self.half,
            self.comb2,
        ]
        effects_set = sum(1 for effect in effects if effect is not None)
        if effects_set != 1:
            raise ValueError(
                f"Exactly one float function type must be set. Found {effects_set} types: {[e.__class__.__name__ for e in effects if e is not None]}."
            )
        return self


# Composite float function configurations
# These still inherit from FloatFunctionTemplate (now empty) and contain FloatFunction
class RepeatFloatFunctionConfig(FloatFunctionTemplate):
    """Repeat function configuration"""
    numberOfTimes: float = Field(
        description="Number of times to repeat the function")
    funcToRepeat: FloatFunction = Field(description="Function to repeat")


class HalfFloatFunctionConfig(FloatFunctionTemplate):
    """Half function configuration"""
    f1: FloatFunction = Field(description="First half function")
    f2: FloatFunction = Field(description="Second half function")


class Comb2FloatFunctionConfig(FloatFunctionTemplate):
    """Combines two float functions with weighted coefficients to create a new function.
    The output is calculated as: output = amount1 * f1(x) + amount2 * f2(x)
    This allows for blending or mixing of two different function behaviors."""
    f1: FloatFunction = Field(
        description="The first function to be combined in the weighted sum")
    amount1: float = Field(
        description=
        "Weight coefficient for the first function. Determines the contribution of f1 to the final output"
    )
    f2: FloatFunction = Field(
        description="The second function to be combined in the weighted sum")
    amount2: float = Field(
        description=
        "Weight coefficient for the second function. Determines the contribution of f2 to the final output"
    )


# Update forward references - still needed for string literal type hints
FloatFunction.model_rebuild()


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


# >>>>>>>>>>>>>>>>>>>>>>>>
# Define the possible worlds and their elements
ELEMENT_WORLDS = {
    "rings": [
        "ring7", "ring8", "ring9", "ring10", "ring11", "ring12"
    ],
    "spirals": [
        "spiral_big", "spiral_small",
    ],
    "orchids": [
        "orchid1", "orchid2", "orchid3",
    ]
}

SEGMENTS_WORLDS = {
    "rings": [
        "centric", "updown", "arc", "ind", "b1", "b2", "rand", "all"
    ],
    # "spiral_big": [
    #     "spiral1", "spiral2", "spiral3", "spiral4", "spiral5", "outline", "spiral6",
    #     "subout1", "subout2", "subout3", "subout4", "subout5", "subout6", "subout7",
    #     "subout8", "subout9", "subout10"
    # ],
    # "spiral_small": [
    "spirals": [
        "spiral1", "spiral2", "spiral3", "outline",
        "subout1", "subout2", "subout3", "subout4", "subout5", "subout6", "subout7",
        "subout8", "subout9", "subout10"
    ],
    "orchids": [
        "leaf1", "leaf2", "stem", "petal1", "petal2", "petal3"
    ]
}

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
    segments: typing.List[str] = Field(
        default_factory=list,
        min_length=1,
        description=
        "Specifies a List of the segments of LEDs to which the effect will be applied."
    )

    # _world: typing.ClassVar[str] = "rings"
    # _world: typing.ClassVar[str] = "spirals"
    # _segments: typing.ClassVar[typing.List[str]] = SEGMENTS_WORLDS.get(_world, [])
    # @classmethod
    # def set_world(cls, world: str):
    #     if world not in SEGMENTS_WORLDS:
    #         raise ValueError(f"Unknown world: {world}")
    #     cls._world = world
    #     cls._segments = SEGMENTS_WORLDS.get(world, [])

    # @model_validator(mode="after")
    # def check_segments_valid_for_world(self):
    #     valid_segments = SEGMENTS_WORLDS.get(self._world, [])
    #     if self.segments not in valid_segments:
    #         raise ValueError(
    #             f"Segment '{self.segments}' is not valid for world '{self._world}'. Valid segments: {valid_segments}"
    #         )
    #     return self


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

    elements: typing.List[str] = Field(
        default_factory=list,
        min_length=1,
        description="Specifies the list of elements to which this effect applies. The valid elements depend on the selected world."
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

    effect_summary: str = Field(
        default="",
        description=
        "A brief summary of what this effect does. Focus on which colors the user see and which patterns and motions (e.g. rapid blinking pink snake, with green b1 segment). Provides a visual overview so that the user can understand which one is it.."
    )

    # _world: typing.ClassVar[str] = "rings"  # default world

    # @classmethod
    # def set_world(cls, world: str):
    #     if world not in ELEMENT_WORLDS:
    #         raise ValueError(f"Unknown world: {world}")
    #     cls._world = world
    #     EffectConfig.set_world(world)

    # @model_validator(mode="after")
    # def check_elements_valid_for_world(self):
    #     valid_elements = ELEMENT_WORLDS.get(self._world, [])
    #     for el in self.elements:
    #         if el not in valid_elements:
    #             raise ValueError(
    #                 f"Element '{el}' is not valid for world '{self._world}'. Valid elements: {valid_elements}"
    #             )
    #     return self

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
        default_factory=list, 
        min_length=1,
        description="List of effects in the animation.")
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

    animation: AnimationProto = Field(default_factory=AnimationProto,
                                      description="The whole animation.")
    name: str = Field(
        default="",
        description=(
            "The animation title. If the user specifies the song name as 'some_name', "
            "you should put 'some_name' here. The name must not contain spaces or special characters; "
            "it should only include letters, numbers, and underscores (_)."))

    # def __init__(self, *args, world: str = "rings", **data):
    #     if world not in ELEMENT_WORLDS:
    #         raise ValueError(f"Unknown world: {world}")
    #     EffectProto.set_world(world)
    #     super().__init__(*args, **data)


from typing import Literal, List, Optional, Type
from pydantic import create_model, Field

# --- World Configurations and Base Schemas ---
# ELEMENT_WORLDS = {
#     "rings": ("ring7", "ring8", "ring9"),
#     "spirals": ("spiral_big", "spiral_small"),
# }
# SEGMENTS_WORLDS = {
#     "rings": ("centric", "updown", "arc"),
#     "spirals": ("spiral1", "spiral2", "outline"),
# }

# --- The Factory Function (Pydantic V1 Compatible) ---
def create_kivsee_schema(world: str) -> Type[BaseModel]:
    """
    Factory that builds and returns a dynamic Pydantic CLASS using
    Pydantic V1 patterns.
    """
    if world not in ELEMENT_WORLDS or world not in SEGMENTS_WORLDS:
        raise ValueError(f"Unknown world: {world}")

    # Create the dynamic Literal types for validation
    # ElementLiterals = Literal[ELEMENT_WORLDS[world]]
    # SegmentLiterals = Literal[SEGMENTS_WORLDS[world]]
    ElementLiterals = Literal[*ELEMENT_WORLDS[world]]
    SegmentLiterals = Literal[*SEGMENTS_WORLDS[world]]

    
    # --- Use create_model for all dynamic classes ---
    # Only override the specific fields that need to be dynamic (elements, segments)

    # Build EffectConfig fields, replacing 'segments' with Literal-based field
    effect_config_fields = {
        name: (field.annotation, field.default if field.default is not None else ...)
        for name, field in EffectConfig.model_fields.items()
        if name != "segments"
    }
    effect_config_fields["segments"] = (List[SegmentLiterals], Field(..., min_length=1))
    DynamicEffectConfig = create_model(
        'DynamicEffectConfig',
        **effect_config_fields
    )

    # Build EffectProto fields, replacing 'elements' and 'effect_config'
    effect_proto_fields = {
        name: (field.annotation, field.default if field.default is not None else ...)
        for name, field in EffectProto.model_fields.items()
        if name not in ("elements", "effect_config")
    }
    effect_proto_fields["elements"] = (List[ElementLiterals], Field(..., min_length=1))
    effect_proto_fields["effect_config"] = (DynamicEffectConfig, Field(default_factory=DynamicEffectConfig))
    DynamicEffectProto = create_model(
        'DynamicEffectProto',
        **effect_proto_fields
    )

    # Build AnimationProto fields (no dynamic fields needed)
    animation_proto_fields = {
        name: (field.annotation, field.default if field.default is not None else ...)
        for name, field in AnimationProto.model_fields.items()
        if name != "effects"
    }
    animation_proto_fields["effects"] = (List[DynamicEffectProto], Field(..., min_length=1))
    DynamicAnimationProto = create_model(
        'DynamicAnimationProto',
        **animation_proto_fields
    )

    # Final model creation remains the same
    FinalKivseeSchema = create_model(
        f'KivseeSchema_{world.capitalize()}',
        animation=(DynamicAnimationProto, Field(default_factory=DynamicAnimationProto)),
        name=(str, Field(default=""))
    )
    
    return FinalKivseeSchema
