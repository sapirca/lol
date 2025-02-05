import os
from animation.frameworks.sequence import Sequence

import xml.etree.ElementTree as ET

from controller.constants import XLIGHTS_ANIMATION_SUFFIX, XLIGHTS_TEMP_ANIMATION_FILE


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

    def build_temp_animation_file_path(self, output_dir):
        temp_file_path = os.path.join(output_dir, XLIGHTS_TEMP_ANIMATION_FILE)
        return os.path.abspath(temp_file_path)

    def get_suffix(self):
        return XLIGHTS_ANIMATION_SUFFIX
