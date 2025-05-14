from abc import ABC, abstractmethod

from pydantic import BaseModel


class Framework(ABC):

    @abstractmethod
    def get_response_scheme_obj(self) -> BaseModel:
        pass
