# core/caleb_task_manager.py

import os
import subprocess
from core.memory_manager import MemoryManager
from core.dependency_manager import DependencyManager
from core.caleb_builder import CalebBuilder

class CalebTaskManager:
    """
    Handles interpretation of text commands,
    dispatches actions, and returns responses
    for the CLI or GUI.
    """

    def __init__(self):
        self.memory = MemoryManager()
        self.dependency_manager = DependencyManager(self.memory)
        self.builder = CalebBuilder()

    def handle_task(self, text, memory_manager=None, dependency_manager=None):
        """
        Interprets a string command and executes
        builder actions accordingly.
        """

        command = text.lower().strip()

        # -----------------------
        # Core commands
        # -----------------------

        if command == "help":
            return (
                "Available commands:\n"
                "- help\n"
                "- install dependencies\n"
                "- setup project\n"
                "- build basics\n"
                "- show memory\n"
                "- clear memory\n"
                "- exit\n"
            )

        # Install dependencies
        if "install dependencies" in command:
            self.dependency_manager.run_full_check()
            return "Dependencies installation triggered."

        # Initialize studio folders
        if "setup project" in command or "initialize" in command:
            self.builder.run_build_pipeline()
            return "Studio base directories and models setup started."

        # Show saved memory
        if "show memory" in command:
            mem = self.memory.get_memory()
            if not mem:
                return "Memory is currently empty."
            return f"Memory contents:\n{mem}"

        # Clear memory
        if "clear memory" in command:
            self.memory._initialize_memory()
            return "Memory cleared."

        # Exit command
        if "exit" in command or "quit" in command:
            return "Exiting task manager..."

        # Fallback if nothing matched
        return "Unknown command. Type 'help' for a list of commands."
