from animation.frameworks.sequence import Sequence
import os

from constants import ANIMATION_OUT_TEMP_DIR, KIVSEE_ANIMATION_SUFFIX, KIVSEE_TEMP_ANIMATION_FILE


class KivseeSequence(Sequence):

    def __init__(self, sequence_path=None):
        self.sequence_path = sequence_path
        self.sequence_data = None
        self.steps = []
        self._load_sequence_skeleton()

    def get_animation_filename(self):
        working_dir = os.path.dirname(os.path.abspath(__file__))
        return super().build_temp_animation_file_path(
            working_dir, KIVSEE_TEMP_ANIMATION_FILE)

    def _load_sequence_skeleton(self):
        """Load the initial sequence skeleton."""
        # try:
        #     with open(self.sequence_path, 'r') as file:
        #         self.sequence_data = file.read()
        #     # Ensure the first step is the skeleton sequence
        #     self.steps.append({"step": 0, "sequence": self.sequence_data})
        # except Exception as e:
        #     raise RuntimeError(f"Error loading sequence skeleton: {e}")

        #         self.steps.append({"step": 0, "sequence": """{
        #     "effects": [{
        #         "effect_config": {
        #             "start_time": 0,
        #             "end_time": 500,
        #             "segments": "all"
        #         },
        #         "const_color": {
        #             "color": {
        #                 "hue": 1.0,
        #                 "sat": 1.0,
        #                 "val": 0.3
        #             }
        #         }
        #     }],
        #     "duration_ms": 1000,
        #     "num_repeats": 0
        # }"""})
        pass

    def get_suffix(self):
        return KIVSEE_ANIMATION_SUFFIX
