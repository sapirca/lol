import xml.etree.ElementTree as ET

class SequenceManager:
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
        """Add a new sequence to the manager."""
        step = {"step": step_number, "sequence": sequence_xml}
        self.steps.append(step)

    def get_latest_sequence(self):
        """Return the latest sequence available."""
        if not self.steps:
            return None
        return self.steps[-1]["sequence"]
