import os
import json

class MemoryManager:
    def __init__(self, memory_file="memory.json"):
        self.memory_file = memory_file
        self.memory = self._load_memory()

    def _load_memory(self):
        """Load memory from JSON file, safely initialize if empty or invalid."""
        if not os.path.exists(self.memory_file):
            # Create empty memory file
            with open(self.memory_file, "w") as f:
                json.dump({}, f)
            return {}

        try:
            with open(self.memory_file, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            # Backup broken memory file
            os.rename(self.memory_file, self.memory_file + ".bak")
            with open(self.memory_file, "w") as f:
                json.dump({}, f)
            return {}

    def save_memory(self):
        """Save current memory to file."""
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=4)

    def get(self, key, default=None):
        return self.memory.get(key, default)

    def set(self, key, value):
        self.memory[key] = value
        self.save_memory()
