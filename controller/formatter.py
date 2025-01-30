from animation.sequence_manager import SequenceManager
from logger import Logger
from controller.constants import XSEQUENCE_TAG

class Formatter:
    def __init__(self, logger : Logger, sequence_manager: SequenceManager):
        """
        Initializes the Formatter class.

        :param logger: Logger instance for logging events.
        :param sequence_manager: SequenceManager instance to manage animation sequences.
        """
        self.logger = logger
        self.sequence_manager = sequence_manager

    def build_messages(self):
        """
        Constructs a list of messages for the LLM context based on the logs.

        :return: List of formatted message dictionaries for the LLM.
        """
        messages = []
        
        for log in self.logger.logs:
            if log['context']:
                role = self._determine_role(log['tag'])
                messages.append({"role": role, "content": log['content']})
        
        latest_sequence = self.sequence_manager.get_latest_sequence()
        if latest_sequence:
            messages.append({
                "role": "system",
                "content": f"Latest Animation Sequence ({XSEQUENCE_TAG}):\n{latest_sequence}"
            })
        
        return messages

    def _determine_role(self, tag):
        """
        Determines the role of a message based on its tag.

        :param tag: The tag associated with the log message.
        :return: Corresponding role for the message.
        """
        role_mapping = {
            "initial_prompt_context": "system",
            "initial_animation": "system",
            "user_input": "user",
            "assistant": "assistant"
        }
        
        return role_mapping.get(tag, "system")
