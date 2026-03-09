"""
MEMORY MANAGER
==============

This module provides persistent memory for CalebStudioBuilder.

It records:

- files created
- completed tasks
- pending tasks
- installed dependencies
- downloaded models
- API keys (only references, not plaintext keys if avoidable)

The memory is stored as JSON so it can persist between runs.
"""

import json
import os
import datetime


class MemoryManager:

    def __init__(self, memory_path="memory/caleb_memory.json"):

        self.memory_path = memory_path

        directory = os.path.dirname(self.memory_path)

        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.exists(self.memory_path):
            self._initialize_memory()

        self.memory = self._load_memory()

    def _initialize_memory(self):

        initial_memory = {
            "created_files": [],
            "completed_tasks": [],
            "pending_tasks": [],
            "installed_dependencies": [],
            "downloaded_models": [],
            "api_keys_requested": [],
            "build_stage": 0,
            "last_updated": self._timestamp()
        }

        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(initial_memory, f, indent=4)

    def _load_memory(self):

        with open(self.memory_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_memory(self):

        self.memory["last_updated"] = self._timestamp()

        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=4)

    def add_created_file(self, path):

        if path not in self.memory["created_files"]:
            self.memory["created_files"].append(path)
            self.save_memory()

    def add_completed_task(self, task):

        if task not in self.memory["completed_tasks"]:
            self.memory["completed_tasks"].append(task)
            self.save_memory()

    def add_pending_task(self, task):

        if task not in self.memory["pending_tasks"]:
            self.memory["pending_tasks"].append(task)
            self.save_memory()

    def complete_task(self, task):

        if task in self.memory["pending_tasks"]:
            self.memory["pending_tasks"].remove(task)

        self.add_completed_task(task)

    def add_dependency(self, dependency):

        if dependency not in self.memory["installed_dependencies"]:
            self.memory["installed_dependencies"].append(dependency)
            self.save_memory()

    def add_downloaded_model(self, model):

        if model not in self.memory["downloaded_models"]:
            self.memory["downloaded_models"].append(model)
            self.save_memory()

    def request_api_key(self, service):

        if service not in self.memory["api_keys_requested"]:
            self.memory["api_keys_requested"].append(service)
            self.save_memory()

    def get_memory(self):
        return self.memory

    def set_build_stage(self, stage):

        self.memory["build_stage"] = stage
        self.save_memory()

    def get_build_stage(self):
        return self.memory["build_stage"]

    def _timestamp(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
