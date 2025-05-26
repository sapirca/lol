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
        If the key exists, the new value will be concatenated with the existing value using newlines.
        If the key doesn't exist, a new entry will be created.
        
        :param key: The key to store the value under
        :param value: The value to store
        """
        if not isinstance(value, str):
            value = str(value)

        if key in self.memory:
            # If key exists, concatenate with newline
            existing_value = self.memory[key]
            if not isinstance(existing_value, str):
                existing_value = str(existing_value)
            # Split by newlines, remove duplicates while preserving order
            unique_lines = []
            seen = set()
            for line in (existing_value + '\n' + value).split('\n'):
                if line.strip() and line not in seen:
                    seen.add(line)
                    unique_lines.append(line)
            self.memory[key] = '\n'.join(unique_lines)
        else:
            # If key doesn't exist, create new entry
            self.memory[key] = value

        self._save_memory()

    def read_from_memory(self, key):
        """Reads a value from memory using the given key.
        
        :param key: The key to read the value for
        :return: The value stored under the key, or None if the key doesn't exist
        :raises: ValueError if the key is None or empty
        """
        if not key or not isinstance(key, str):
            raise ValueError("Key must be a non-empty string")

        return self.memory.get(key)

    def remove_from_memory(self, key):
        """Removes a key-value pair from memory.
        
        :param key: The key to remove
        :return: True if the key was found and removed, False otherwise
        :raises: ValueError if the key is None or empty
        """
        if not key or not isinstance(key, str):
            raise ValueError("Key must be a non-empty string")

        if key in self.memory:
            del self.memory[key]
            self._save_memory()
            return True
        return False

    def shutdown(self):
        """Save memory to file during shutdown."""
        self._save_memory()


# manager = MemoryManager(framework_name)

# # Write some data to memory
# manager.write_to_memory("key1", "First entry")
# manager.write_to_memory("key2", "Second entry")

# # Retrieve and print the entire memory
# print(manager.get_memory())
