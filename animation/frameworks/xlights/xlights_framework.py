from animation.frameworks.framework import Framework
from animation.frameworks.xlights.xlights_sequence import XlightsSequence
import os
import xml.etree.ElementTree as ET
from controller.constants import XLIGHTS_HOUSE_PATH, XLIGHTS_KNOWLEDGE_PATH, XLIGHTS_TEMP_ANIMATION_FILE, XLIGHTS_SEQUENCE_PATH


class XLightsFramework(Framework):

    def __init__(self):
        self.sequence_manager = XlightsSequence(XLIGHTS_SEQUENCE_PATH)

    def build_temp_animation_file_path(self, output_dir):
        temp_file_path = os.path.join(output_dir, XLIGHTS_TEMP_ANIMATION_FILE)
        return os.path.abspath(temp_file_path)

    def get_world_structure(self):
        try:
            tree = ET.parse(XLIGHTS_HOUSE_PATH)
            root = tree.getroot()
            return ET.tostring(root, encoding='unicode')
        except Exception as e:
            print(f"Logger: Error loading house configuration: {e}")
            return f"Xlights: Error loading house configuration: {e}"

    def get_domain_knowledge(self):
        try:
            with open(XLIGHTS_KNOWLEDGE_PATH, 'r') as file:
                content = file.read()
            return content
        except Exception as e:
            print(f"Logger: Error reading domain knowledge: {e}")
            return f"Xlights: Error reading domain knowledge: {e}"

    def get_latest_sequence(self):
        return self.sequence_manager.get_latest_sequence()

    def get_all_sequences(self):
        return self.sequence_manager.get_all_sequences()

    def load_sequences(self, animations):
        self.sequence_manager.load_sequences(animations)

    def add_sequence(self, step_number, animation_sequence):
        return self.sequence_manager.add_sequence(step_number,
                                                  animation_sequence)
