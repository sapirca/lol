from controller.constants import ANIMATION_OUT_TEMP_DIR, XLIGHTS_SEQUENCE_PATH, KIVSEE_SEQUENCE_PATH
from animation.frameworks.kivsee.kivsee_framework import KivseeFramework
from animation.frameworks.framework import Framework
from animation.frameworks.xlights.xlights_framework import XLightsFramework
from animation.frameworks.xlights.xlights_sequence import XlightsSequence
from animation.frameworks.kivsee.kivsee_sequence import KivseeSequence
from animation.frameworks.sequence import Sequence
from animation.knowledge import knowledge_prompts
import os

class AnimationManager:
    def __init__(self, framework_name, message_streamer):
        self.framework_name = framework_name
        self.framework: Framework = None
        self.sequence_manager: Sequence = None
        self.message_streamer = message_streamer
        self._load_animation_framework()

    def _load_animation_framework(self):
        if self.framework_name == 'kivsee':
            self.framework = KivseeFramework()
            self.sequence_manager = KivseeSequence(KIVSEE_SEQUENCE_PATH)
        elif self.framework_name == 'xlights':
            self.framework = XLightsFramework()
            self.sequence_manager = XlightsSequence(XLIGHTS_SEQUENCE_PATH)
        else:
            raise ValueError(f"Unsupported framework: {self.framework_name}")

    def get_prompt(self):
        return self.framework.get_prompt()

    def process_animation(self, animation_sequence):
        self.framework.process_animation(animation_sequence)

    def store_temp_animation(self, animation_sequence):
        output_dir = ANIMATION_OUT_TEMP_DIR
        os.makedirs(output_dir, exist_ok=True)
        
        temp_file_path = self.framework.build_temp_animation_file_path(output_dir)
        abs_temp_file_path = os.path.abspath(temp_file_path)

        with open(abs_temp_file_path, "w") as temp_file:
            temp_file.write(animation_sequence)

        return abs_temp_file_path

    def delete_temp_file(self, file_path):
        absolute_path = os.path.abspath(file_path)
        try:
            if os.path.exists(absolute_path):
                os.remove(absolute_path)
                if not os.path.exists(absolute_path):
                    print(f"Logger: Temp file {absolute_path} was successfully deleted.")
                else:
                    print(f"Logger: Error: Temp file {absolute_path} still exists after deletion attempt.")
            else:
                print(f"Logger: Temp file {absolute_path} does not exist.")
        except Exception as e:
            print(f"Logger: An error occurred while deleting {absolute_path}: {e}")

    def get_world_structure(self):
        return self.framework.get_world_structure()

    def get_general_knowledge(self):
        return "".join(knowledge_prompts)
    
    def get_domain_knowledge(self):
        return self.framework.get_domain_knowledge()

    def get_latest_sequence(self):
        return self.sequence_manager.get_latest_sequence()

    def get_all_sequences(self):
        return self.sequence_manager.get_all_sequences()

    def load_sequences(self, animations):
        self.sequence_manager.load_sequences(animations)

    def add_sequence(self, step_number, animation_sequence):
        return self.sequence_manager.add_sequence(step_number, animation_sequence)
