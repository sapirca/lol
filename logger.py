import os
import json
from datetime import datetime, timedelta
import threading


def count_words(text):
    """Utility function to count words in a given text."""
    return len(text.split())


def estimate_tokens(words):
    """Estimate the number of tokens based on word count."""
    return int(words * 1.33 + 0.5)  # Round up to nearest integer


class Logger:

    def __init__(self, log_dir="logs", snapshot_interval=30):
        """Initialize the logger with optional periodic snapshot caching."""
        self.log_dir = log_dir
        self.logs = []  # Unified log storage for all messages
        self.snapshot_file = os.path.join(log_dir, "snapshot.json")
        os.makedirs(log_dir, exist_ok=True)
        self.snapshot_interval = snapshot_interval
        self._start_periodic_snapshot()

    def add_message(self, tag, content, visible, context):
        """Add a message to the log with specific tags and flags."""
        words = count_words(content)
        tokens_estimation = estimate_tokens(words)
        self.logs.append({
            "tag": tag,
            "content": content,
            "visible": visible,
            "context": context,
            "words": words,
            "tokens_estimation": tokens_estimation,
            "timestamp": datetime.now().isoformat()
        })

    def add_log(self, content):
        """Add a system log with predefined tags and flags."""
        words = count_words(content)
        tokens_estimation = estimate_tokens(words)
        self.logs.append({
            "tag": "info_log",
            "content": content,
            "visible": False,
            "context": False,
            "words": words,
            "tokens_estimation": tokens_estimation,
            "timestamp": datetime.now().isoformat()
        })

    def error(self, content):
        """Log an error message."""
        words = count_words(content)
        tokens_estimation = estimate_tokens(words)
        self.logs.append({
            "tag": "error_log",
            "content": content,
            "visible": True,
            "context": False,
            "words": words,
            "tokens_estimation": tokens_estimation,
            "timestamp": datetime.now().isoformat()
        })

    def finalize(self):
        """Save all logs to a file and add a summary log."""
        total_sent_tokens = sum(log["tokens_estimation"] for log in self.logs
                                if log["context"])
        total_received_tokens = sum(log["tokens_estimation"]
                                    for log in self.logs if not log["context"])

        # Add a system log for the overall sent and received tokens
        self.add_log(
            f"Total sent tokens: {total_sent_tokens}, Total received tokens: {total_received_tokens}"
        )

        with open(self.snapshot_file, "w") as file:
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

    def _start_periodic_snapshot(self):
        """Start a thread for periodic snapshot caching."""

        def snapshot_loop():
            while True:
                self._cache_snapshot()
                threading.Event().wait(self.snapshot_interval)

        thread = threading.Thread(target=snapshot_loop, daemon=True)
        thread.start()

    def _cache_snapshot(self):
        """Periodically cache the snapshot to disk."""
        try:
            with open(self.snapshot_file, "w") as file:
                json.dump(self.logs, file, indent=4)
            self.add_log("Periodic snapshot cached successfully.")
        except Exception as e:
            self.add_log(f"Error during periodic snapshot: {e}")
