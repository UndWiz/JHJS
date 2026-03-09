"""
DEPENDENCY MANAGER
=================
Automatically installs and checks dependencies for CalebStudioBuilder.

Features:
- Python package management via pip
- Optional system package support
- Tracks installed packages in memory_manager
- Safe installation with logging and error handling
"""

import subprocess
import sys
import importlib
from core.memory_manager import MemoryManager

class DependencyManager:

    def __init__(self, memory: MemoryManager):
        self.memory = memory

    def is_installed(self, package_name):
        try:
            importlib.import_module(package_name)
            return True
        except ImportError:
            return False

    def install_python_package(self, package_name, version=None):
        pkg = f"{package_name}=={version}" if version else package_name
        if self.is_installed(package_name):
            print(f"[INFO] {pkg} already installed.")
            self.memory.add_dependency(pkg)
            return True

        print(f"[INFO] Installing {pkg}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            self.memory.add_dependency(pkg)
            print(f"[SUCCESS] Installed {pkg}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to install {pkg}: {e}")
            return False

    def install_system_package(self, package_name):
        """
        Example: sudo apt install package_name -y
        """
        print(f"[INFO] Installing system package {package_name}...")
        try:
            subprocess.check_call(["sudo", "apt", "install", package_name, "-y"])
            print(f"[SUCCESS] Installed system package {package_name}")
            self.memory.add_dependency(package_name)
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to install system package {package_name}: {e}")
            return False

    def install_core_dependencies(self):
        """
        List all Python & system packages required by the studio
        """
        python_packages = [
            "torch",
            "diffusers",
            "transformers",
            "chromadb",
            "fastapi",
            "uvicorn",
            "requests",
            "pillow",
            "opencv-python",
            "tqdm",
            "rich",
            "PySimpleGUI",
            "scipy",
            "scikit-learn",
            "matplotlib",
            "accelerate"
        ]

        system_packages = [
            "git",
            "ffmpeg",
            "imagemagick"
        ]

        print("[INFO] Installing Python packages...")
        for pkg in python_packages:
            self.install_python_package(pkg)

        print("[INFO] Installing system packages...")
        for spkg in system_packages:
            self.install_system_package(spkg)

        print("[INFO] All core dependencies processed.")

if __name__ == "__main__":
    mm = MemoryManager()
    dm = DependencyManager(mm)
    dm.install_core_dependencies()
