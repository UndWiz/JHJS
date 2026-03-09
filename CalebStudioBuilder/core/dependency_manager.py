"""
DEPENDENCY MANAGER
==================
Automatically checks and installs Python packages, system libs, and AI frameworks.
Designed for CalebStudioBuilder.
"""

import subprocess
import sys
import os

class DependencyManager:

    def __init__(self):
        self.python_packages = [
            "torch",
            "diffusers",
            "transformers",
            "accelerate",
            "onnxruntime",
            "faiss-cpu",
            "chromadb",
            "opencv-python",
            "tqdm",
            "sentence-transformers",
            "gradio"
        ]
        self.system_packages = [
            "git",
            "wget",
            "curl",
            "ffmpeg",
            "python3-venv",
            "build-essential"
        ]

    # ------------------------------
    # 1. Check Python packages
    # ------------------------------
    def check_python_package(self, package):
        try:
            __import__(package)
            print(f"[OK] Python package {package} is installed")
            return True
        except ImportError:
            print(f"[MISSING] Python package {package}")
            return False

    # ------------------------------
    # 2. Install Python package
    # ------------------------------
    def install_python_package(self, package):
        print(f"[INSTALLING] {package} via pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)

    # ------------------------------
    # 3. Check all Python packages
    # ------------------------------
    def check_all_python(self):
        for pkg in self.python_packages:
            if not self.check_python_package(pkg):
                self.install_python_package(pkg)

    # ------------------------------
    # 4. Check system packages
    # ------------------------------
    def check_system_package(self, package):
        result = subprocess.run(["which", package], capture_output=True)
        if result.returncode == 0:
            print(f"[OK] System package {package} is installed")
            return True
        else:
            print(f"[MISSING] System package {package}")
            return False

    # ------------------------------
    # 5. Suggest install for missing system packages
    # ------------------------------
    def install_system_package(self, package):
        print(f"[ACTION REQUIRED] Please install {package} via your package manager (apt/yum/pacman)")

    # ------------------------------
    # 6. Check all system packages
    # ------------------------------
    def check_all_system(self):
        for pkg in self.system_packages:
            if not self.check_system_package(pkg):
                self.install_system_package(pkg)

    # ------------------------------
    # 7. Verify GPU / AI framework
    # ------------------------------
    def check_gpu(self):
        try:
            import torch
            if torch.cuda.is_available():
                print(f"[GPU DETECTED] {torch.cuda.get_device_name(0)}")
            else:
                print("[INFO] No CUDA GPU detected, will use CPU")
        except Exception as e:
            print(f"[ERROR] GPU check failed: {e}")

    # ------------------------------
    # 8. Run full dependency check
    # ------------------------------
    def run_full_check(self):
        print("[INFO] Checking system packages...")
        self.check_all_system()
        print("[INFO] Checking Python packages...")
        self.check_all_python()
        print("[INFO] Checking GPU / AI frameworks...")
        self.check_gpu()
        print("[SUCCESS] Dependency check complete!")

# ------------------------------
# 9. Run as script
# ------------------------------
if __name__ == "__main__":
    dm = DependencyManager()
    dm.run_full_check()
