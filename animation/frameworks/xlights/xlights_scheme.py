from pydantic import BaseModel, Field
from typing import List, Optional


class Head(BaseModel):
    version: str
    author: Optional[str]
    author_email: Optional[str]
    author_website: Optional[str]
    song: str
    artist: str
    album: str
    MusicURL: Optional[str]
    comment: Optional[str]
    sequenceTiming: str
    sequenceType: str
    mediaFile: str
    sequenceDuration: float
    imageDir: Optional[str]


class DataLayer(BaseModel):
    lor_params: int
    channel_offset: int
    num_channels: int
    num_frames: int
    data: str
    source: str
    name: str


class DisplayElement(BaseModel):
    collapsed: int
    type: str
    name: str
    visible: int
    views: Optional[str]
    active: Optional[int]


class ElementEffect(BaseModel):
    type: str
    name: str


class TimingTag(BaseModel):
    number: int
    position: int


class XlightsScheme(BaseModel):
    BaseChannel: int
    ChanCtrlBasic: int
    ChanCtrlColor: int
    FixedPointTiming: int
    ModelBlending: bool
    head: Head
    nextid: int
    DataLayers: List[DataLayer]
    DisplayElements: List[DisplayElement]
    ElementEffects: List[ElementEffect]
    lastView: int
    TimingTags: List[TimingTag]
