from animation.frameworks.sequence import Sequence
import os
import json
from controller.constants import CONCEPTUAL_ANIMATION_SUFFIX, CONCEPTUAL_TEMP_ANIMATION_FILE


class ConceptualSequence(Sequence):

    def __init__(self, sequence_path):
        self.sequence_path = sequence_path
        self.sequence_data = None
        self.steps = []
        # self._load_sequence_skeleton()

    def build_temp_animation_file_path(self, output_dir):
        temp_file_path = os.path.join(output_dir,
                                      CONCEPTUAL_TEMP_ANIMATION_FILE)
        return os.path.abspath(temp_file_path)

    def _load_sequence_skeleton(self):
        """Load the initial sequence skeleton."""
        # try:
        #     with open(self.sequence_path, 'r') as file:
        #         self.sequence_data = json.load(file)
        #     # Ensure the first step is the skeleton sequence
        #     self.steps.append({"step": 0, "sequence": self.sequence_data})
        # except Exception as e:
        #     raise RuntimeError(f"Error loading sequence skeleton: {e}")

    def get_suffix(self):
        return CONCEPTUAL_ANIMATION_SUFFIX
