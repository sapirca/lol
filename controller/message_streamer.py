import os
import json
from datetime import datetime, timedelta
import threading
from constants import TIME_FORMAT, LOG_INTERVAL_IN_SECONDS, MESSAGE_SNAPSHOT_FILE
from constants import SNAPSHOTS_DIR


def count_words(text):
    """Utility function to count words in a given text."""
    return len(text.split())


def estimate_tokens(words):
    """Estimate the number of tokens based on word count."""
    return int(words * 1.33 + 0.5)  # Round up to nearest integer


class MessageStreamer:  # Updated class name

    def __init__(self,
                 snapshots_dir=SNAPSHOTS_DIR,
                 snapshot_interval=LOG_INTERVAL_IN_SECONDS):
        """Initialize the MessageStreamer with optional periodic snapshot caching."""

        self.snapshots_dir = snapshots_dir
        os.makedirs(self.snapshots_dir, exist_ok=True)

        self.messages = []  # Unified log storage for all messages
        # self.msgs_full_path = os.path.join(self.snapshots_dir, MESSAGE_SNAPSHOT_FILE)

        self.periodic_snapshot = os.path.join(self.snapshots_dir,
                                              "preiodic_snapshot.json")
        self.snapshot_interval = snapshot_interval
        self._start_periodic_snapshot()

    def add_message(self, tag, content, visible, context):
        """Add a message to the log with specific tags and flags."""
        words = count_words(content)
        tokens_estimation = estimate_tokens(words)
        timestamp = datetime.now().strftime(TIME_FORMAT)
        self.messages.append({
            "tag": tag,
            "content": content,
            "visible": visible,
            "context": context,
            "words": words,
            "tokens_estimation": tokens_estimation,
            "timestamp": timestamp
        })

    def add_log(self, content):
        """Add a system log with predefined tags and flags."""
        words = count_words(content)
        tokens_estimation = estimate_tokens(words)
        self.messages.append({
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
        self.messages.append({
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
        total_sent_tokens = sum(message["tokens_estimation"]
                                for message in self.messages
                                if message["context"])
        total_received_tokens = sum(message["tokens_estimation"]
                                    for message in self.messages
                                    if not message["context"])

        # Add a system log for the overall sent and received tokens
        self.add_log(
            f"Total sent tokens: {total_sent_tokens}, Total received tokens: {total_received_tokens}"
        )

        # TODO remove this method?

        # with open(self.msgs_full_path, "w") as file:
        #     json.dump(self.messages, file, indent=4)

    def load(self, file_name):
        """Load logs from a specified file."""
        if os.path.exists(file_name):
            with open(file_name, "r") as file:
                self.messages = json.load(file)
        else:
            raise FileNotFoundError(f"Log file '{file_name}' does not exist.")

    def get_context_to_llm(self):
        """Retrieve the full context for LLM, including logs marked as context."""
        return "\n".join(message["content"] for message in self.messages
                         if message["context"])

    def get_visible_chat(self):
        """Retrieve all visible messages as a dictionary."""
        return {
            message["tag"]: message["content"]
            for message in self.messages if message["visible"]
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
        """Periodically cache the snapshot to disk.
        We write this only for backups incase the main file is lost or corrupted.
        Read manually if system crashes."""

        try:
            with open(self.periodic_snapshot, "w") as file:
                json.dump(self.messages, file, indent=4)
        except Exception as e:
            self.add_log(f"Error during periodic snapshot: {e}")
