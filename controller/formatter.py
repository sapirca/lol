from animation.frameworks.xlights.xlights_sequence import XlightsSequence
from controller.message_streamer import MessageStreamer
from animation.animation_manager import AnimationManager
from memory.memory_manager import MemoryManager
from music.song_provider import SongProvider
from typing import Optional, Dict, Any
from prompts.main_prompt import intro_prompt


class Formatter:

    def __init__(self,
                 message_streamer: MessageStreamer,
                 animation_manager: AnimationManager,
                 memory_manager: MemoryManager,
                 song_provider: SongProvider,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initializes the Formatter class.

        :param message_streamer: MessageStreamer instance of the messages stream.
        :param animation_manager: AnimationManager instance to manage animations.
        :param memory_manager: MemoryManager instance to manage memory.
        :param song_provider: SongProvider instance to get song information.
        :param config: Optional configuration dictionary.
        """
        self.message_streamer = message_streamer
        self.animation_manager = animation_manager
        self.memory_manager = memory_manager
        self.song_provider = song_provider
        self.config = config or {}

    def build_messages(self):
        """
        Constructs a list of messages for the LLM context based on the messages.

        :return: List of formatted message dictionaries for the LLM.
        """
        messages = []

        # Build prompt content

        prompt_content = []
        if intro_prompt:
            prompt_content.append("# Your Task\n")
            prompt_content.append(intro_prompt)

        # TODO(Sapir): Rename to get_timing_knowledge
        timing_knowledge = self.animation_manager.get_general_knowledge()
        if timing_knowledge:
            prompt_content.append("## Timing Knowledge\n")
            prompt_content.append(timing_knowledge)

        messages.append({
            "role": "system",
            "content": "\n".join(prompt_content)
        })

        # Add memory info
        memory = self.memory_manager.get_memory()
        if memory:
            messages.append({
                "role": "system",
                "content": f"# Your Memory: {memory}"
            })

        # Add song info if available
        try:
            song_name = self.config.get("song_name")
            if song_name:
                song_info = self.song_provider.get_song_structure(song_name)
                if song_info:
                    messages.append({
                        "role":
                        "system",
                        "content":
                        f"# The Song Structure:\n {song_info}"
                    })
        except Exception as e:
            # Log error but continue without song info
            print(f"Error getting song info: {e}")

        # Add message history
        for message in self.message_streamer.messages:
            if message['context']:
                role = self._determine_role(message['tag'])
                messages.append({"role": role, "content": message['content']})

        # Add the latest animation sequence
        latest_sequence = self.animation_manager.get_latest_sequence()
        if latest_sequence:
            messages.append({
                "role":
                "system",
                "content":
                f"# Animation Sequence:\n Make sure to maintain a consistent animation, only change the part of animation that the user asked for. In case of doubt, ask the user for clarification. The latest animation sequence is:\n {latest_sequence}"
            })

        # Save the whole prompt to a file
        with open("prompt_before_sending.md", "w") as file:
            for message in messages:
                # file.write(f"{message['role']}: {message['content']}\n")
                file.write(f"\n{'='*80}\n")
                file.write(f"Role: {message['role']}\n\n")
                file.write(f"{message['content']}\n")

        return messages

    def _determine_role(self, tag):
        """
        Determines the role based on the message tag.

        :param tag: The message tag.
        :return: The corresponding role for the message.
        """
        role_mapping = {
            'user_input': 'user',
            'assistant': 'assistant',
            'system': 'system',
            'action_results': 'system',
            'initial_prompt_context': 'system'
        }
        return role_mapping.get(tag, 'system')
