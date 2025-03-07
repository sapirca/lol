from pydantic import BaseModel, Field, model_validator
from typing import List, Literal, Union, Optional


class Coloring(BaseModel):
    type: str = Field(
        description=
        "Coloring effects define the base color of an element. If no coloring effect is applied, the element will not be visible.",
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

        # Optional[int] = Field(
        #     description="Hue is measured in degrees from 0 to 360. Required for constant type, not needed for rainbow",
        #     default=None)
        # Optional[str] = Field(
        #     description="predefined hue values. Set hue for constant type, not needed for rainbow",
        #           enum=["HUE_RED", "HUE_ORANGE", "HUE_YELLOW", "HUE_GREEN", "HUE_AQUA", "HUE_BLUE", "HUE_PURPLE", "HUE_PINK"],
        #             default=None)


class Brightness(BaseModel):
    type: str = Field(
        description=
        "Brightness effects modify the intensity of the light over time. If no brightness effect is set, brightness remains constant. No need to put this field if no brightness effect is needed.",
        enum=["fadeIn", "fadeOut", "blink", "fadeInOut", "fadeOutIn"])
    value: Optional[float] = Field(description="Required if type is constant",
                                   default=None,
                                   ge=0.3,
                                   le=0.8)


class Motion(BaseModel):
    type: str = Field(
        description=
        "Motion effects create movement in the animation. If no motion is needed, dont include this field. The motion effect added intrest to the viewer, and a sense of movement to the lights.",
        enum=["snake", "snakeInOut"])


class Beat(BaseModel):
    beat_start: int = Field(
        description=
        "The beat at which the effect starts. Song is 4/4 time signature. 1 bar = 4 beats, 1 beat = 1/4 of a bar. Song BPM is XYZ, then 60/XYZ seconds per beat. 120 BPM = 0.5 seconds per beat. 1 Bar = 4 beats = 0.5*2 = 2 seconds. Carefully examin the units in the requests and do the converation to beats. This field is in beats only. E.g convert bars 3-4 to beats 12-16."
    )
    beat_end: int = Field(
        description=
        "The beat at which the effect ends. Song is 4/4 time signature. 1 bar = 4 beats, 1 beat = 1/4 of a bar. Song BPM is XYZ, then 60/XYZ seconds per beat. 120 BPM = 0.5 seconds per beat. 1 Bar = 4 beats = 0.5*2 = 2 seconds. Carefully examin the units in the requests and do the converation to beats. This field is in beats only. E.g convert bars 3-4 to beats 12-16."
    )
    elements: List[str] = Field(
        description=
        "Name of individual Elements (ring1-ring12) or groups of elements (all, odd, even, left, right, center, outer) affected during this time period. Groups select all element in the group (e.g., 'odd' selects odd-numbered rings, 'left' selects left-side rings).",
        enum=[
            "ring1", "ring2", "ring3", "ring4", "ring5", "ring6", "ring7",
            "ring8", "ring9", "ring10", "ring11", "ring12", "all", "odd",
            "even", "left", "right", "center", "outer"
        ])
    coloring: Coloring
    brightness: Optional[Brightness] = None
    motion: Optional[Motion] = None

    # @model_validator(mode='before')
    # def check_coloring_dependency(cls, values):
    #     motion = values.get('motion')
    #     coloring = values.get('coloring')
    #     if motion and not coloring:
    #         raise ValueError(
    #             'If motion is provided, coloring must also be provided.')
    #     return values


class Animation(BaseModel):
    name: str = Field(description="The song title")
    duration: float = Field(description="Total length in **seconds**.", ge=0)
    beats: List[Beat]


class ResponseSchema(BaseModel):
    instruction: str = Field(
        description=
        "The instruction that was given to the model to generate this response."
    )
    name: str
    animation: Animation
    reasoning: str = Field(
        description=
        "A brief explanation of the reasoning behind the animation, or why these changes in the animation were made."
    )
