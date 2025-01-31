from animation.frameworks.sequence import Sequence

import xml.etree.ElementTree as ET

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
            self.steps.append({"step": 0, "sequence": ET.tostring(self.sequence_data, encoding="unicode")})
        except Exception as e:
            raise RuntimeError(f"Error loading sequence skeleton: {e}")

    def add_sequence(self, step_number, sequence_xml):
        """Add a new sequence to the manager and log the update."""
        step = {"step": step_number, "sequence": sequence_xml}
        self.steps.append(step)
        return f"Animation updated for step {step_number}"

    def get_latest_sequence(self):
        """Return the latest sequence available."""
        if not self.steps:
            return None
        return self.steps[-1]["sequence"]

    def get_all_sequences(self):
        """Return all sequences as a list."""
        return [step["sequence"] for step in self.steps]

    def load_sequences(self, sequences):
        """Load sequences from a list."""
        self.steps = []
        for i, sequence in enumerate(sequences):
            self.steps.append({"step": i, "sequence": sequence})
