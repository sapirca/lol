# chat_history.py

import os
import json
from datetime import datetime

class ChatHistory:
    """
    Class to manage chat history and prepare context efficiently for LLMs.
    """
    def __init__(self, snapshot_dir="chats/snapshots", final_dir="chats/finals"):
        self.history = []  # List to store history as dictionaries with 'role' and 'content'.
        self.snapshot_dir = snapshot_dir
        self.final_dir = final_dir

        # Ensure directories exist
        os.makedirs(self.snapshot_dir, exist_ok=True)
        os.makedirs(self.final_dir, exist_ok=True)

    def add_message(self, role, content):
        """Add a message to the history."""
        self.history.append({"role": role, "content": content})
        self._cache_history()

    def get_context(self):
        """Prepare the chat history to be sent to the LLM, excluding animation tags."""
        return "\n".join([
            f"<{msg['role']}>: {msg['content']}"
            for msg in self.history
            if msg["role"] != "animation"
        ])

    def _cache_history(self):
        """Save chat history to a snapshot file."""
        snapshot_file = os.path.join(self.snapshot_dir, "chat_history_snapshot.json")
        with open(snapshot_file, "w") as cache:
            json.dump(self.history, cache, indent=4)

    def load_chat_history(self, file_path=None):
        """Load a specific chat history file (snapshot or final)."""
        if not file_path:
            file_path = os.path.join(self.snapshot_dir, "chat_history_snapshot.json")

        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                self.history = json.load(file)
        else:
            raise FileNotFoundError(f"The file {file_path} does not exist.")

    def finalize(self):
        """Write the final state of the chat history to a log file on exit."""
        log_filename = os.path.join(self.final_dir, datetime.now().strftime("final_chat_log_%Y-%m-%d_%H-%M-%S.json"))
        with open(log_filename, "w") as log_file:
            json.dump(self.history, log_file, indent=4)
