from pydantic import BaseModel
from animation.frameworks.conceptual.response_schema import ResponseSchema
from animation.frameworks.framework import Framework
from animation.frameworks.conceptual.conceptual_sequence import ConceptualSequence
import os
import json
from controller.constants import CONCEPTUAL_HOUSE_PATH, CONCEPTUAL_KNOWLEDGE_PATH, CONCEPTUAL_PROMPT, CONCEPTUAL_SEQUENCE_PATH


class ConceptualFramework(Framework):

    def __init__(self):
        self.sequence_manager = ConceptualSequence(CONCEPTUAL_SEQUENCE_PATH)

    def get_world_structure(self):
        try:
            with open(CONCEPTUAL_HOUSE_PATH, 'r') as file:
                house_structure = file.read()
            return house_structure
        except Exception as e:
            print(f"Logger: Error loading house configuration: {e}")
            raise RuntimeError(
                "Conceptual: Failed to load the house configuration") from e

    def get_domain_knowledge(self):
        try:
            # with open(CONCEPTUAL_KNOWLEDGE_PATH, 'r') as file:
            with open(CONCEPTUAL_PROMPT, 'r') as file:
                content = file.read()
            return content
        except Exception as e:
            print(f"Logger: Error reading domain knowledge: {e}")
            return "Conceptual domain knowledge"

    def get_response_scheme_obj(self) -> BaseModel:
        return ResponseSchema()
