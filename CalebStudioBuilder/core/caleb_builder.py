# core/caleb_builder.py
import os
from core.memory_manager import MemoryManager
from core.file_manager import FileManager
from core.dependency_manager import DependencyManager

class CalebBuilder:
    def __init__(self, base_path="./data"):
        # Initialize memory
        self.memory_manager = MemoryManager()
        
        # Ensure base path exists for file operations
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)
        
        # Initialize file manager with correct path
        self.file_manager = FileManager(self.base_path)
        
        # Initialize dependency manager with memory reference
        self.dependency_manager = DependencyManager(self.memory_manager)

    def build_task(self, task_name, params):
        # Example builder function
        print(f"Building task: {task_name} with params: {params}")
        # Save to memory and files as needed
        self.memory_manager.memory[task_name] = params
        self.file_manager.save_task(task_name, params)
