from pydantic import BaseModel, Field
from typing import List, Optional


class SummarizationResponse(BaseModel):
    """Schema for summarization responses."""
    summary: str = Field(
        description=
        "A concise summary of the conversation, including main topics, key decisions, and important context."
    )
    animation_summary: str = Field(
        description=
        "A natural language description of all animation sequences created, without any code."
    )
    pending_tasks: List[str] = Field(
        default_factory=list,
        description=
        "List of any pending tasks or unresolved questions from the conversation."
    )
