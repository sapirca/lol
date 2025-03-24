from typing import List, Optional
from pydantic import BaseModel, Field


class TimeFrame(BaseModel):
    start: float = Field(description="Start time")
    end: float = Field(description="End time")


class AnimationUpdate(BaseModel):
    time_frame: TimeFrame
    scene_description: str = Field(
        description="Description of the scene within the time frame")


class SummarizationResult(BaseModel):
    summarized_animation: List[AnimationUpdate] = Field(
        description=
        "Array of animation descriptions, each with a time frame and scene description"
    )
