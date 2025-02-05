from abc import ABC, abstractmethod


class Framework(ABC):

    def __init__(self):
        self.prompts = self.load_prompts()

    @abstractmethod
    def get_world_structure(self):
        # Abstract method to enforce implementation in subclasses
        pass

    @abstractmethod
    def get_domain_knowledge(self):
        # Abstract method to enforce implementation in subclasses
        pass
