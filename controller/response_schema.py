from pydantic import BaseModel, Field, model_validator
from typing import Set, Union, List


class Coloring(BaseModel):
    type: str = Field(
        description=
        "Coloring effects define the base color of an element. If no coloring effect is applied, the element will not be visible.",
        enum=["constant", "rainbow"])
    hue: Union[float, None] = Field(
        description="Required for constant type, not needed for rainbow",
        default=None)


class Brightness(BaseModel):
    type: str = Field(
        description=
        "Brightness effects modify the intensity of the light over time. If no brightness effect is set, brightness remains constant. No need to put this field if no brightness effect is needed.",
        enum=["fadeIn", "fadeOut", "blink", "fadeInOut", "fadeOutIn"])
    value: Union[float,
                 None] = Field(description="Required if type is constant",
                               default=None,
                               ge=0,
                               le=1)


class Motion(BaseModel):
    type: str = Field(
        description=
        "Motion effects create movement in the animation. If no motion is needed, dont include this field. The motion effect added intrest to the viewer, and a sense of movement to the lights.",
        enum=["snake", "snakeInOut"])


class Beat(BaseModel):
    beat_start: float = Field(description="Starting beat")
    beat_end: float = Field(description="Ending beat")
    elements: Set[Union[str]] = Field(
        description=
        "Name of individual Elements (ring1-ring12) or groups of elements (all, odd, even, left, right, center, outer) affected during this time period. Groups select all element in the group (e.g., 'odd' selects odd-numbered rings, 'left' selects left-side rings).",
        enum=[
            "ring1", "ring2", "ring3", "ring4", "ring5", "ring6", "ring7",
            "ring8", "ring9", "ring10", "ring11", "ring12", "all", "odd",
            "even", "left", "right", "center", "outer"
        ])
    coloring: Coloring
    brightness: Brightness = None
    motion: Motion = None

    @model_validator(mode='before')
    def check_coloring_dependency(cls, values):
        motion = values.get('motion')
        coloring = values.get('coloring')
        if motion and not coloring:
            raise ValueError(
                'If motion is provided, coloring must also be provided.')
        return values


class Animation(BaseModel):
    name: str = Field(description="The song title")
    duration: float = Field(description="Total length in **seconds**.", ge=0)
    beats: List[Beat]


class ResponseSchema(BaseModel):
    name: str
    reasoning: str = Field(
        description=
        "A brief explanation of the reasoning behind the animation, or why these changes in the animation were made."
    )
    animation: Animation
