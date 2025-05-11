from pydantic import BaseModel
from animation.frameworks.kivsee.renderer.render import Render
from constants import ANIMATION_OUT_TEMP_DIR, XLIGHTS_SEQUENCE_PATH, CONCEPTUAL_SEQUENCE_PATH
from animation.frameworks.kivsee.kivsee_framework import KivseeFramework
from animation.frameworks.framework import Framework
from animation.frameworks.xlights.xlights_framework import XLightsFramework
from animation.frameworks.xlights.xlights_sequence import XlightsSequence
from animation.frameworks.kivsee.kivsee_sequence import KivseeSequence
from animation.frameworks.conceptual.conceptual_framework import ConceptualFramework
from animation.frameworks.conceptual.conceptual_sequence import ConceptualSequence
from animation.frameworks.sequence import Sequence
from animation.knowledge import knowledge_prompts
import os


class AnimationManager:

    def __init__(self, framework_name, message_streamer):
        self.framework_name = framework_name
        self.framework: Framework = None
        # TODO(sapir): rename to sequence_db
        self.sequence_manager: Sequence = None
        self.message_streamer = message_streamer
        self._load_animation_framework()

    def _load_animation_framework(self):
        if self.framework_name == 'kivsee':
            self.sequence_manager = KivseeSequence()
            self.framework = KivseeFramework()
            self.renderer = Render()
        elif self.framework_name == 'xlights':
            self.sequence_manager = XlightsSequence(XLIGHTS_SEQUENCE_PATH)
            self.framework = XLightsFramework()
            self.renderer = None
        elif self.framework_name == 'conceptual':
            self.sequence_manager = ConceptualSequence(
                CONCEPTUAL_SEQUENCE_PATH)
            self.framework = ConceptualFramework()
            self.renderer = None
        else:
            raise ValueError(f"Unsupported framework: {self.framework_name}")

    def get_prompt(self):
        return self.framework.get_prompt()

    def save_tmp_animation(self, animation_sequence: str):
        abs_temp_file_path = self.sequence_manager.get_animation_filename()
        with open(abs_temp_file_path, "w") as temp_file:
            temp_file.write(animation_sequence)
        return abs_temp_file_path

    def delete_temp_file(self, file_path):
        absolute_path = os.path.abspath(file_path)
        try:
            if os.path.exists(absolute_path):
                os.remove(absolute_path)
                if not os.path.exists(absolute_path):
                    print(
                        f"Logger: Temp file {absolute_path} was successfully deleted."
                    )
                else:
                    print(
                        f"Logger: Error: Temp file {absolute_path} still exists after deletion attempt."
                    )
            else:
                print(f"Logger: Temp file {absolute_path} does not exist.")
        except Exception as e:
            print(
                f"Logger: An error occurred while deleting {absolute_path}: {e}"
            )

    def get_world_structure(self):
        return self.framework.get_world_structure()

    def replay(self):
        if self.renderer:
            self.renderer.load_and_print_animation()
        else:
            print("Replay method is not available for this framework.")

    def render(self, animation_sequence):
        if self.renderer:
            self.renderer.render(animation_data=animation_sequence)
        else:
            print("Render method is not available for this framework.")

    def get_general_knowledge(self):
        return "".join(knowledge_prompts)

    def get_domain_knowledge(self):
        return self.framework.get_domain_knowledge()

    def get_latest_sequence(self):
        latest_sequence = self.sequence_manager.get_latest_sequence()
        if not latest_sequence:
            return None
        return f"{latest_sequence}"
        # return f"<animation> {self.sequence_manager.get_latest_sequence()} </animation>"
        return f"{self.sequence_manager.get_latest_sequence()}"

    def get_all_sequences(self):
        return self.sequence_manager.get_all_sequences()

    def load_sequences(self, animations):
        self.sequence_manager.load_sequences(animations)

    def add_sequence(self, step_number, animation_sequence):
        return self.sequence_manager.add_sequence(step_number,
                                                  animation_sequence)

    def save_all_animations(self, snapshot_dir, animation_suffix):
        """Save all animations to the specified directory."""
        all_animations = self.get_all_sequences()
        animations_dir = os.path.join(snapshot_dir, "animations")
        os.makedirs(animations_dir, exist_ok=True)
        for i, animation in enumerate(all_animations, start=1):
            animation_file = os.path.join(animations_dir,
                                          f"animation_{i}.{animation_suffix}")
            with open(animation_file, "w") as file:
                file.write(animation)

    def get_suffix(self):
        return self.sequence_manager.get_suffix()

    def get_response_object(self) -> BaseModel:
        return self.framework.get_response_scheme_obj()
