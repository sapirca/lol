# logger.py
import os
import json
from datetime import datetime

class Logger:
    def __init__(self, log_dir="logs", snapshot_file="logs/snapshot.json"):
        self.log_dir = log_dir
        self.snapshot_file = snapshot_file
        self.logs = []  # Unified log storage for all messages
        os.makedirs(log_dir, exist_ok=True)

    def add_message(self, tag, content):
        """Add a message to the log with a specific tag."""
        self.logs.append({"tag": tag, "content": content, "timestamp": datetime.now().isoformat()})

    def snapshot(self):
        """Save a snapshot of the logs to a file."""
        with open(self.snapshot_file, "w") as snapshot:
            json.dump(self.logs, snapshot, indent=2)

    def finalize(self):
        """Write all logs to a final file."""
        final_file = os.path.join(self.log_dir, datetime.now().strftime("final_log_%Y-%m-%d_%H-%M-%S.json"))
        with open(final_file, "w") as final:
            json.dump(self.logs, final, indent=2)

    def dump_readable(self, filepath):
        """Dump logs to a file in a human-readable format."""
        with open(filepath, "w") as readable:
            for log in self.logs:
                readable.write(f"[{log['timestamp']}] <{log['tag']}>: {log['content']}\n")

    def get_visible_chat(self):
        """
        Retrieve only the visible messages from the logger.
        Visible messages are those tagged with 'lol_visible_user', 'lol_visible_assistant', and 'lol_visible_system'.
        """
        visible_tags = {"lol_visible_user", "lol_visible_assistant", "lol_visible_system"}
        visible_chat = [
            f"<{log['tag']}>: {log['content']}" 
            for log in self.logs if log["tag"] in visible_tags
        ]
        return visible_chat

    def get_context_to_llm(self):
        """
        Retrieve the context to be sent to the LLM.
        This filters all messages with '_context' in their tag.
        """
        llm_context = [
            f"{log['content']}"
            for log in self.logs if "_context" in log["tag"]
        ]
        return "\n".join(llm_context)