import os
import json

MEMORY_BASE_PATH = "/Users/sapir/repos/lol/memory"


class MemoryManager:

    def __init__(self, framework_name):
        """Initialize the MemoryManager with a specific framework's memory file.
        
        :param framework_name: Name of the framework to manage memory for
        """
        self.memory_file_path = os.path.join(MEMORY_BASE_PATH, framework_name,
                                             "my_memory.json")
        os.makedirs(os.path.dirname(self.memory_file_path), exist_ok=True)
        self.memory = {}
        self._load_memory()

    def _load_memory(self):
        """Load memory from file if it exists."""
        try:
            if os.path.exists(self.memory_file_path):
                with open(self.memory_file_path, 'r') as file:
                    self.memory = json.load(file)
            else:
                self.memory = {}
                self._save_memory()  # Initialize empty memory file
        except Exception as e:
            print(f"Error loading memory: {e}")
            self.memory = {}

    def _save_memory(self):
        """Save current memory to file."""
        try:
            with open(self.memory_file_path, 'w') as file:
                json.dump(self.memory, file, indent=4)
        except Exception as e:
            print(f"Error saving memory: {e}")

    def get_memory(self):
        """Returns the entire content of the memory."""
        return self.memory

    def write_to_memory(self, key, value):
        """Writes a key-value pair to memory and saves to file.
        
        :param key: The key to store the value under
        :param value: The value to store
        """
        self.memory[key] = value
        self._save_memory()

    def shutdown(self):
        """Save memory to file during shutdown."""
        self._save_memory()


# manager = MemoryManager(framework_name)

# # Write some data to memory
# manager.write_to_memory("key1", "First entry")
# manager.write_to_memory("key2", "Second entry")

# # Retrieve and print the entire memory
# print(manager.get_memory())
