class SequenceManager:

    def __init__(self):
        self.sequences = []
        self.current_step = 0

    def add_sequence(self, sequence):
        self.sequences.append(sequence)
        self.current_step += 1

    def get_latest_sequence(self):
        if not self.sequences:
            return None
        return self.sequences[-1]

    def get_latest_sequence_with_step(self):
        """Returns tuple of (latest_sequence, current_step) or None if no sequence exists."""
        if not self.sequences:
            return None
        return self.sequences[-1], self.current_step

    def get_current_step(self):
        """Returns the current step number."""
        return self.current_step

    def get_all_sequences(self):
        return self.sequences

    def clear_sequences(self):
        self.sequences = []
        self.current_step = 0
