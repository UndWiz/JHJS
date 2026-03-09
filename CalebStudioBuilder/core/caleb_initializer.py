"""
CALEB INITIALIZER
=================
Main entry point for CalebStudioBuilder.
Sets up memory, dependencies, folder structure, and optional Cloud Mentor integration.
"""

import os
from memory_manager import MemoryManager
from file_manager import FileManager
from dependency_manager import DependencyManager

class CalebInitializer:

    def __init__(self):
        print("[INIT] Starting Caleb Studio Builder...")
        self.memory = MemoryManager()
        self.file_manager = FileManager(self.memory)
        self.dependency_manager = DependencyManager(self.memory)
        self.project_root = os.path.expanduser("~/CalebStudioProjects")
        self.caleb_core = os.path.join(self.project_root, "CalebCore")
        self.enable_cloud_mentor = False

    def setup_project_folders(self):
        print(f"[INFO] Creating project root at {self.project_root}...")
        os.makedirs(self.project_root, exist_ok=True)
        os.makedirs(self.caleb_core, exist_ok=True)
        print(f"[INFO] Setting up core subfolders...")
        self.file_manager.create_folder(os.path.join(self.caleb_core, "models"))
        self.file_manager.create_folder(os.path.join(self.caleb_core, "memory"))
        self.file_manager.create_folder(os.path.join(self.caleb_core, "logs"))
        self.file_manager.create_folder(os.path.join(self.caleb_core, "temp"))
        self.file_manager.create_folder(os.path.join(self.caleb_core, "scripts"))
        print("[SUCCESS] Project folders created.")

    def install_dependencies(self):
        print("[INFO] Installing all required dependencies...")
        self.dependency_manager.install_core_dependencies()
        print("[SUCCESS] Dependencies checked and installed.")

    def cloud_mentor_prompt(self):
        answer = input("Do you want to enable Cloud Mentor integration? (y/N): ").strip().lower()
        self.enable_cloud_mentor = answer == "y"
        if self.enable_cloud_mentor:
            print("[INFO] Cloud Mentor enabled.")
        else:
            print("[INFO] Cloud Mentor disabled. Local Caleb only.")

    def initialize(self):
        self.setup_project_folders()
        self.install_dependencies()
        self.cloud_mentor_prompt()
        print("[READY] CalebStudioBuilder is ready to start building your studio!")

if __name__ == "__main__":
    initializer = CalebInitializer()
    initializer.initialize()
