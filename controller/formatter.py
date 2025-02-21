from animation.frameworks.xlights.xlights_sequence import XlightsSequence
from controller.message_streamer import MessageStreamer
from animation.animation_manager import AnimationManager


class Formatter:

    def __init__(self, message_streamer: MessageStreamer,
                 animation_manager: AnimationManager):
        """
        Initializes the Formatter class.

        :param message_streamer: MessageStreamer instance of the messages stream.
        :param animation_manager: AnimationManager instance to manage animations.
        """
        self.message_streamer = message_streamer
        self.animation_manager = animation_manager

    def build_messages(self):
        """
        Constructs a list of messages for the LLM context based on the messages.

        :return: List of formatted message dictionaries for the LLM.
        """
        messages = []

        for message in self.message_streamer.messages:
            if message['context']:
                role = self._determine_role(message['tag'])
                messages.append({"role": role, "content": message['content']})

        # TODO : Do not add the latest animation? Reconsider later
        # latest_sequence = self.animation_manager.get_latest_sequence()
        # if latest_sequence:
        #     messages.append({
        #         "role":
        #         "system",
        #         "content":
        #         f"Animation Sequence: \n{latest_sequence}"
        #     })

        return messages

    def _determine_role(self, tag):
        """
        Determines the role of a message based on its tag.

        :param tag: The tag associated with the message.
        :return: Corresponding role for the message.
        """
        role_mapping = {
            "initial_prompt_context": "system",
            "initial_animation": "system",
            "user_input": "user",
            "assistant": "assistant"
        }

        return role_mapping.get(tag, "system")
