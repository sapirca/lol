from animation.frameworks.framework import Framework
from animation.frameworks.xlights.xlights_sequence import XlightsSequence
import os
import xml.etree.ElementTree as ET
from controller.constants import KIVSEE_HOUSE_PATH, KIVSEE_TEMP_ANIMATION_FILE, KIVSEE_SEQUENCE_PATH

class KivseeFramework(Framework):
    def __init__(self):
        self.sequence_manager = XlightsSequence(KIVSEE_SEQUENCE_PATH)
        # ...existing code...

    def get_prompt(self):
        return self.prompts.get(self.__class__.__name__.lower(), 'Kivsee prompt')

    def process_animation(self, animation_sequence):
        # Process the animation sequence specific to Kivsee framework
        # ...existing code...
        pass

    def load_animation(self, data):
        # Default loading logic
        pass

    def build_temp_animation_file_path(self, output_dir):
        temp_file_path = os.path.join(output_dir, KIVSEE_TEMP_ANIMATION_FILE)
        return os.path.abspath(temp_file_path)

    def get_world_structure(self):
        try:
            tree = ET.parse(KIVSEE_HOUSE_PATH)
            root = tree.getroot()
            return ET.tostring(root, encoding='unicode')
        except Exception as e:
            print(f"Logger: Error loading house configuration: {e}")
            raise RuntimeError("Failed to parse the house configuration") from e

    def get_domain_knowledge(self):
        # Return domain knowledge specific to Kivsee framework
        return "Kivsee domain knowledge"

    def get_latest_sequence(self):
        return self.sequence_manager.get_latest_sequence()

    def get_all_sequences(self):
        return self.sequence_manager.get_all_sequences()

    def load_sequences(self, animations):
        self.sequence_manager.load_sequences(animations)

    def add_sequence(self, step_number, animation_sequence):
        return self.sequence_manager.add_sequence(step_number, animation_sequence)