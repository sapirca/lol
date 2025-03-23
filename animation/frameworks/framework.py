from abc import ABC, abstractmethod

from pydantic import BaseModel


class Framework(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def get_world_structure(self):
        # Abstract method to enforce implementation in subclasses
        pass

    @abstractmethod
    def get_domain_knowledge(self):
        # Abstract method to enforce implementation in subclasses
        pass

    def get_response_scheme_obj(self) -> BaseModel:
        # Stub implementation
        return None
