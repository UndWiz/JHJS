# core/file_manager.py
import os
import json

class FileManager:
    def __init__(self, base_path):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def save_task(self, task_name, params):
        filepath = os.path.join(self.base_path, f"{task_name}.json")
        with open(filepath, "w") as f:
            json.dump(params, f, indent=2)
