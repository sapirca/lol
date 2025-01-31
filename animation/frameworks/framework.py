from abc import ABC, abstractmethod

class Framework(ABC):
    def __init__(self):
        self.prompts = self.load_prompts()

    def get_prompt(self):
        return self.prompts.get(self.__class__.__name__.lower(), 'Default prompt')

    def extract_animation_from_response(self, response):
        # Default parsing logic
        return response

    def process_animation(self, animation_sequence):
        # Default processing logic
        pass

    def load_animation(self, data):
        # Default loading logic
        pass

    @abstractmethod
    def build_temp_animation_file_path(self, output_dir):
        # Default implementation for building temp animation file path
        pass

    @abstractmethod
    def get_world_structure(self):
        # Abstract method to enforce implementation in subclasses
        pass

    @abstractmethod
    def get_domain_knowledge(self):
        # Abstract method to enforce implementation in subclasses
        pass
