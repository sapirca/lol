# logger.py
import os
import json
from datetime import datetime

class Logger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.logs = []  # Unified log storage for all messages
        os.makedirs(log_dir, exist_ok=True)

    def add_message(self, tag, content, visible, context):
        """Add a message to the log with specific tags and flags."""
        self.logs.append({
            "tag": tag,
            "content": content,
            "visible": visible,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })

    def finalize(self, snapshot_file="logs/snapshot.json"):
        """Save all logs to a file."""
        with open(snapshot_file, "w") as file:
            json.dump(self.logs, file, indent=4)

    def load(self, file_name):
        """Load logs from a specified file."""
        if os.path.exists(file_name):
            with open(file_name, "r") as file:
                self.logs = json.load(file)
        else:
            raise FileNotFoundError(f"Log file '{file_name}' does not exist.")

    def get_context_to_llm(self):
        """Retrieve the full context for LLM, including logs marked as context."""
        return "\n".join(log["content"] for log in self.logs if log["context"])

    def get_visible_chat(self):
        """Retrieve all visible messages as a dictionary."""
        return {
            log["tag"]: log["content"]
            for log in self.logs if log["visible"]
        }
