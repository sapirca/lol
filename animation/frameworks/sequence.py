from abc import ABC, abstractmethod
import os

from constants import ANIMATION_OUT_TEMP_DIR


class Sequence(ABC):

    def add_sequence(self, step_number, sequence):
        """Add a new sequence to the manager and log the update."""
        # TODO(sapir) this is a bag!!! It does not append in the right order ???
        step = {"step": step_number, "sequence": sequence}
        self.steps.append(step)
        return f"Animation updated for step {step_number}"

    def get_latest_sequence(self):
        """Return the latest sequence available."""
        latest_key_val = max(self.steps, key=lambda x: x["step"], default=None)
        if latest_key_val:
            return latest_key_val["sequence"]
        else:
            return None
        # return self.steps[-1]["sequence"] if self.steps else None

    def get_all_sequences(self):
        """Return all sequences as a list."""
        return [step["sequence"] for step in self.steps]

    def load_sequences(self, sequences):
        """Load sequences from a list."""
        self.steps = []
        for i, sequence in enumerate(sequences):
            self.steps.append({"step": i, "sequence": sequence})

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
