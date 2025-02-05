from animation.frameworks.sequence import Sequence
import os


class KivseeSequence(Sequence):

    def __init__(self, sequence_path):
        self.sequence_path = sequence_path
        self.sequence_data = None
        self.steps = []
        self._load_sequence_skeleton()

    def _load_sequence_skeleton(self):
        """Load the initial sequence skeleton."""
        try:
            with open(self.sequence_path, 'r') as file:
                self.sequence_data = file.read()
            # Ensure the first step is the skeleton sequence
            self.steps.append({"step": 0, "sequence": self.sequence_data})
        except Exception as e:
            raise RuntimeError(f"Error loading sequence skeleton: {e}")
