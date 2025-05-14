import os
import json

MEMORY_BASE_PATH = "/Users/sapir/repos/lol/memory"


class MemoryManager:

    def __init__(self, framework_name):
        self.memory_file_path = MEMORY_BASE_PATH + f"/{framework_name}/memory.json"
        if not os.path.exists(self.memory_file_path):
            os.makedirs(os.path.dirname(self.memory_file_path), exist_ok=True)
            with open(self.memory_file_path, 'w') as file:
                json.dump(
                    {}, file
                )  # Initialize an empty JSON object if it doesn't exist

    def get_memory(self):
        """Returns the entire content of the memory file as a dictionary."""
        with open(self.memory_file_path, 'r') as file:
            return json.load(file)

    def write_to_memory(self, key, value):
        """Writes a key-value pair to the memory file."""
        memory = self.get_memory()
        memory[key] = value
        with open(self.memory_file_path, 'w') as file:
            json.dump(memory, file, indent=4)


# manager = MemoryManager(framework_name)

# # Write some data to memory
# manager.write_to_memory("key1", "First entry")
# manager.write_to_memory("key2", "Second entry")

# # Retrieve and print the entire memory
# print(manager.get_memory())
