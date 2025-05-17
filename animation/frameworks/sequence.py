from abc import ABC, abstractmethod
import os

from constants import ANIMATION_OUT_TEMP_DIR


class Sequence(ABC):

    def __init__(self):
        self.sequences = []

    def add_sequence(self, sequence):
        """Add a new sequence to the end of the array and return the current step number."""
        self.sequences.append(sequence)
        return f"Animation sequence added to step {len(self.sequences)}"

    def get_latest_sequence(self):
        """Return the latest sequence available."""
        if not self.sequences:
            return None
        return self.sequences[-1]

    def get_latest_sequence_with_step(self):
        """Returns tuple of (latest_sequence, current_step) or None if no sequence exists."""
        if not self.sequences:
            return None
        return self.sequences[-1], len(self.sequences)

    def get_current_step(self):
        """Returns the current step number (length of sequences array)."""
        return len(self.sequences)

    def get_all_sequences(self):
        """Return all sequences as a list."""
        return self.sequences

    def load_sequences(self, sequences):
        """Load sequences from a list."""
        self.sequences = sequences.copy()

    def get_next_step_number(self):
        """Calculate the next step number based on the current sequences."""
        if self.steps:
            return max(step["step"] for step in self.steps) + 1
        return 1

    @abstractmethod
    def get_suffix(self):
        """Return the animation suffix for the sequence."""
        pass

    @abstractmethod
    def get_animation_filename(self):
        """Build the temporary animation file path."""
        pass

    def build_temp_animation_file_path(self, working_dir, animation_file_name):
        output_dir = ANIMATION_OUT_TEMP_DIR
        full_output_dir = os.path.join(working_dir, output_dir)
        os.makedirs(full_output_dir, exist_ok=True)
        full_temp_file_path = os.path.join(full_output_dir,
                                           animation_file_name)
        return os.path.abspath(full_temp_file_path)
