from pydantic import BaseModel
from animation.frameworks.framework import Framework
from constants import KIVSEE_LEARNING_PATH
from schemes.kivsee_scheme.effects_scheme import KivseeSchema


class KivseeFramework(Framework):

    def __init__(self):
        pass

    def get_response_scheme_obj(self) -> BaseModel:
        return KivseeSchema
