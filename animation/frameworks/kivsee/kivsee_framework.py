from animation.frameworks.framework import Framework
from animation.frameworks.kivsee.kivsee_sequence import KivseeSequence
import os
import xml.etree.ElementTree as ET
from controller.constants import KIVSEE_HOUSE_PATH, KIVSEE_KNOWLEDGE_PATH, KIVSEE_TEMP_ANIMATION_FILE, KIVSEE_SEQUENCE_PATH


class KivseeFramework(Framework):

    def __init__(self):
        self.sequence_manager = KivseeSequence(KIVSEE_SEQUENCE_PATH)

    def build_temp_animation_file_path(self, output_dir):
        temp_file_path = os.path.join(output_dir, KIVSEE_TEMP_ANIMATION_FILE)
        return os.path.abspath(temp_file_path)

    def get_world_structure(self):
        try:
            with open(KIVSEE_HOUSE_PATH, 'r') as file:
                house_structure = file.read()
            return house_structure
        except Exception as e:
            print(f"Logger: Error loading house configuration: {e}")
            raise RuntimeError(
                "Kivsee: Failed to load the house configuration") from e

    def get_domain_knowledge(self):
        try:
            with open(KIVSEE_KNOWLEDGE_PATH, 'r') as file:
                content = file.read()
            return content
        except Exception as e:
            print(f"Logger: Error reading domain knowledge: {e}")
            return "Kivsee domain knowledge"

    def get_latest_sequence(self):
        return self.sequence_manager.get_latest_sequence()

    def get_all_sequences(self):
        return self.sequence_manager.get_all_sequences()

    def load_sequences(self, animations):
        self.sequence_manager.load_sequences(animations)

    def add_sequence(self, step_number, animation_sequence):
        return self.sequence_manager.add_sequence(step_number,
                                                  animation_sequence)
