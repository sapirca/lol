import os
from animation.frameworks.sequence import Sequence

import xml.etree.ElementTree as ET

from constants import ANIMATION_OUT_TEMP_DIR, XLIGHTS_ANIMATION_SUFFIX, XLIGHTS_TEMP_ANIMATION_FILE


class XlightsSequence(Sequence):

    def __init__(self, skeleton_file):
        self.skeleton_file = skeleton_file
        self.sequence_data = None
        self.steps = []
        self._load_sequence_skeleton()

    def _load_sequence_skeleton(self):
        """Load the initial sequence skeleton."""
        try:
            tree = ET.parse(self.skeleton_file)
            self.sequence_data = tree.getroot()
            # Ensure the first step is the skeleton sequence
            self.steps.append({
                "step":
                0,
                "sequence":
                ET.tostring(self.sequence_data, encoding="unicode")
            })
        except Exception as e:
            raise RuntimeError(f"Error loading sequence skeleton: {e}")

    def get_animation_filename(self):
        working_dir = os.path.dirname(os.path.abspath(__file__))
        return super().build_temp_animation_file_path(
            working_dir, XLIGHTS_TEMP_ANIMATION_FILE)

    def get_suffix(self):
        return XLIGHTS_ANIMATION_SUFFIX
