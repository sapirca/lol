# chat_history.py

from constants import MAX_TOKENS

class ChatHistory:
    """
    Class to manage chat history and prepare context efficiently for LLMs.
    """
    def __init__(self, max_tokens=MAX_TOKENS):
        self.history = []  # List to store history as dictionaries with 'role' and 'content'.
        self.max_tokens = max_tokens

    def add_message(self, role, content):
        """Add a message to the history."""
        self.history.append({"role": role, "content": content})
        self._truncate_history()

    def get_context(self):
        """Prepare the chat history to be sent to the LLM."""
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.history])

    def _truncate_history(self):
        """Truncate the history to fit within max_tokens."""
        while self._token_count() > self.max_tokens:
            self.history.pop(0)  # Remove the oldest message

    def _token_count(self):
        """Estimate token count for the current history."""
        return sum(len(msg['content'].split()) for msg in self.history)
