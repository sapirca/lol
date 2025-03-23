from pydantic import BaseModel, Field
from typing import Optional, List

class KivseeSchema(BaseModel):
    id: Optional[int] = Field(None, description="Unique identifier for the schema")
    name: str = Field(..., description="Name of the schema")
    description: Optional[str] = Field(None, description="Description of the schema")
    version: str = Field(..., description="Version of the schema")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags associated with the schema")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "ExampleSchema",
                "description": "This is an example schema",
                "version": "1.0.0",
                "tags": ["example", "schema"]
            }
        }