from pydantic import BaseModel, Field, model_validator
from typing import List, Literal, Union, Optional


class Coloring(BaseModel):
    type: str = Field(
        description=
        "Coloring effects define the base color of an element. If no coloring effect is applied, the element will not be visible. When adding a coloring effect, the LEDs will be lit with a default brightness of 1.0. To adjust it, add a brightness effect.",
        enum=["constant", "rainbow"])
    hue: Optional[Union[float, Literal[
        "RED", "ORANGE", "YELLOW", "GREEN", "AQUA", "BLUE", "PURPLE",
        "PINK"]]] = Field(
            description=
            "The hue value in HSV describes the base color. When represented as a float from 0.0 to 1.0, 0.0 and 1.0 both represent red, as they are the start and end of the color wheel. The values in between transition through the other colors of the spectrum. Required for constant type, not needed for rainbow. Can be a float from 0.0 to 1.0, or one of the predefined color names: RED, ORANGE, YELLOW, GREEN, AQUA, BLUE, PURPLE, PINK.",
            default=None)
    # RED = 0.0, ORANGE = 0.125, YELLOW = 0.250, GREEN = 0.376, AQUA = 0.502, BLUE = 0.627, PURPLE = 0.752, PINK = 0.878, RED = 1.0

    @model_validator(mode='after')
    def check_hue(self):
        if self.type == "constant" and self.hue is None:
            raise ValueError("Hue is required for 'constant' coloring type.")
        if self.type == "rainbow" and self.hue is not None:
            raise ValueError(
                "Hue should not be provided for 'rainbow' coloring type.")
        return self


class Brightness(BaseModel):
    type: str = Field(
        description=
        "Brightness effects modify the intensity of the light over time. If no brightness effect is set, brightness remains constant. No need to include this field if no brightness changes are needed. Coloring effects lit elements with default brightness of 1.0",
        enum=[
            "constant", "fadeIn", "fadeOut", "blink", "fadeInOut", "fadeOutIn"
        ])
    factor_value: Optional[float] = Field(
        description=
        "Required if type is constant. This value is a multiplication factor of the current brightness. A value of 0.5 decreases the current brightness by half.",
        default=None,
        ge=0.0,
        le=1.0)


class Motion(BaseModel):
    type: str = Field(
        description=
        "Motion effects create movement in the animation. If no motion is needed, do not include this field. The motion effect adds interest to the viewer and a sense of movement to the lights.",
        enum=["snake", "snakeInOut"])


class Beat(BaseModel):
    beat_start: int = Field(
        description=
        "The beat at which the effect starts. The song starts at Beat 0 and Bar 0. All songs are in 4/4 or 3/4 time signature, meaning that 1 bar = 4 beats, 1 beat = 1/4 of a bar. If a song BPM is XYZ, then it takes 60/XYZ seconds per beat. For example, 120 BPM = 0.5 seconds per beat. 1 Bar = 4 beats = 0.5*4 = 2 seconds per bar. Carefully examine the units in the requests and convert them to beats. This field is in beats only. For example, convert bars 3-4 to beats 12-16.",
        ge=0)
    beat_end: int = Field(
        description=
        "The beat at which the effect ends. For beat_end=4, the effect will be rendered until and including beat 3, but not including beat 4. The song starts at Beat 0 and Bar 0. All songs are in 4/4 or 3/4 time signature, meaning that 1 bar = 4 beats, 1 beat = 1/4 of a bar. If a song BPM is XYZ, then it takes 60/XYZ seconds per beat. For example, 120 BPM = 0.5 seconds per beat. 1 Bar = 4 beats = 0.5*4 = 2 seconds per bar. Carefully examine the units in the requests and convert them to beats. This field is in beats only. For example, convert bars 3-4 to beats 12-16.",
        ge=0)
    elements: List[str] = Field(
        description=
        "Names of individual elements (ring1-ring12) or groups of elements (all, odd, even, left, right, center, outer) affected during this time period. Groups select all elements in the group (e.g., 'odd' selects odd-numbered rings, 'left' selects left-side rings).",
        enum=[
            "ring1", "ring2", "ring3", "ring4", "ring5", "ring6", "ring7",
            "ring8", "ring9", "ring10", "ring11", "ring12", "all", "odd",
            "even", "left", "right", "center", "outer"
        ])
    mapping: Optional[List[str]] = Field(
        description=
        "Optionally, you can light only a subgroup of pixels of an element or reorder the LEDs, which affects the order of colors and movement. You can use this field to increase the variety and interest in effects. If no value is set, the entire element will be lit in the default physical order of LEDs.",
        enum=[
            "centric", "updown", "arc", "ind", "1_pixel_every_4",
            "1_pixel_every_2"
        ])
    coloring: Coloring
    brightness: Optional[Brightness] = None
    motion: Optional[Motion] = None


class Animation(BaseModel):
    name: str = Field(description="The song title.")
    duration: float = Field(description="Total length in **seconds**.", ge=0)
    beats: List[Beat]


class ResponseSchema(BaseModel):
    name: str
    animation: Animation
    reasoning: str = Field(
        description=
        "A brief explanation of the reasoning behind the animation, or why these changes in the animation were made."
    )
    instruction: str = Field(
        description=
        "The instruction that was given to the model to generate this response."
    )
