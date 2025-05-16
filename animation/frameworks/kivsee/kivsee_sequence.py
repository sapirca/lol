from animation.frameworks.sequence import Sequence
import os

from constants import ANIMATION_OUT_TEMP_DIR, KIVSEE_ANIMATION_SUFFIX, KIVSEE_TEMP_ANIMATION_FILE


class KivseeSequence(Sequence):

    def __init__(self, sequence_path=None):
        super().__init__()
        self.sequence_path = sequence_path
        self.sequence_data = None
        self.steps = []

    def get_animation_filename(self):
        working_dir = os.path.dirname(os.path.abspath(__file__))
        return super().build_temp_animation_file_path(
            working_dir, KIVSEE_TEMP_ANIMATION_FILE)

    def get_suffix(self):
        return KIVSEE_ANIMATION_SUFFIX
