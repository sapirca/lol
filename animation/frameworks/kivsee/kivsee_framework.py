from typing import Type
from pydantic import BaseModel
from animation.frameworks.framework import Framework
from constants import KIVSEE_LEARNING_PATH
from schemes.kivsee_scheme import effects_scheme
# import KivseeSchema


class KivseeFramework(Framework):

    def __init__(self, config=None):
        self.config = config or {}
        # Set the world in the scheme if provided
        self.world = self.config.get("world", "rings")
        # KivseeSchema.set_world(world)

    # def get_response_scheme_obj(self) -> BaseModel:
    #     return KivseeSchema


    def get_response_scheme_obj(self) -> BaseModel:
        return effects_scheme.create_kivsee_schema(self.world)
        
    