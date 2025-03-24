from animation.frameworks.sequence import Sequence
import os
import json
from constants import ANIMATION_OUT_TEMP_DIR, CONCEPTUAL_ANIMATION_SUFFIX, CONCEPTUAL_TEMP_ANIMATION_FILE


class ConceptualSequence(Sequence):

    def __init__(self, sequence_path):
        self.sequence_path = sequence_path
        self.sequence_data = None
        self.steps = []
        # self._load_sequence_skeleton()

    def get_animation_filename(self):
        working_dir = os.path.dirname(os.path.abspath(__file__))
        return super().build_temp_animation_file_path(
            working_dir, CONCEPTUAL_TEMP_ANIMATION_FILE)

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
