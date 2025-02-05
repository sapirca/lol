from abc import ABC, abstractmethod


class Sequence(ABC):

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
