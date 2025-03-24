from animation.frameworks.sequence import Sequence
import os

from controller.constants import KIVSEE_ANIMATION_SUFFIX, KIVSEE_TEMP_ANIMATION_FILE


class KivseeSequence(Sequence):

    def __init__(self, sequence_path):
        self.sequence_path = sequence_path
        self.sequence_data = None
        self.steps = []
        self._load_sequence_skeleton()

    def build_temp_animation_file_path(self, output_dir):
        temp_file_path = os.path.join(output_dir, KIVSEE_TEMP_ANIMATION_FILE)
        return os.path.abspath(temp_file_path)

    def _load_sequence_skeleton(self):
        """Load the initial sequence skeleton."""
        # try:
        #     with open(self.sequence_path, 'r') as file:
        #         self.sequence_data = file.read()
        #     # Ensure the first step is the skeleton sequence
        #     self.steps.append({"step": 0, "sequence": self.sequence_data})
        # except Exception as e:
        #     raise RuntimeError(f"Error loading sequence skeleton: {e}")

        self.steps.append({"step": 0, "sequence": """{
    "effects": [{
        "effect_config": {
            "start_time": 0,
            "end_time": 500,
            "segments": "all"
        },
        "const_color": {
            "color": {
                "hue": 1.0,
                "sat": 1.0,
                "val": 0.3
            }
        }
    }],
    "duration_ms": 1000,
    "num_repeats": 0
}"""})

    def get_suffix(self):
        return KIVSEE_ANIMATION_SUFFIX
