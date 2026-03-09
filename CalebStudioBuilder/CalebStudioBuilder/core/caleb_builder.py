"""
CALEB BUILDER
=============
Engine that builds Jack Hole Jackery Studio locally.
Manages AI models, assets, and automations.
"""

import os
import sys
import subprocess
from core.memory_manager import MemoryManager
from core.file_manager import FileManager
from core.dependency_manager import DependencyManager

class CalebBuilder:

    def __init__(self, project_root="~/CalebStudioProjects", enable_cloud_mentor=False):
        self.project_root = os.path.expanduser(project_root)
        self.caleb_core = os.path.join(self.project_root, "CalebCore")
        self.memory = MemoryManager()
        self.file_manager = FileManager(self.memory)
        self.dependency_manager = DependencyManager(self.memory)
        self.enable_cloud_mentor = enable_cloud_mentor
        self.models_folder = os.path.join(self.caleb_core, "models")
        self.temp_folder = os.path.join(self.caleb_core, "temp")

    # ------------------------------
    # 1. Prepare directories
    # ------------------------------
    def setup_directories(self):
        print(f"[INFO] Preparing directories under {self.caleb_core}...")
        self.file_manager.create_folder(self.models_folder)
        self.file_manager.create_folder(self.temp_folder)
        print("[SUCCESS] Core directories ready.")

    # ------------------------------
    # 2. Install or verify models
    # ------------------------------
    def install_models(self):
        print("[INFO] Installing AI models...")
        model_urls = {
            "stable_diffusion_1.5": "https://huggingface.co/CompVis/stable-diffusion-v1-5",
            "stable_diffusion_2.1": "https://huggingface.co/stabilityai/stable-diffusion-2-1",
            "sdxl_base": "https://huggingface.co/stabilityai/sdxl-base",
            "anim_diff": "https://huggingface.co/animate-diff/anim-diffusion"
        }

        for name, url in model_urls.items():
            model_path = os.path.join(self.models_folder, name)
            if not os.path.exists(model_path):
                print(f"[INFO] Downloading {name} from {url}...")
                subprocess.run(["git", "clone", url, model_path])
            else:
                print(f"[INFO] {name} already exists.")

        print("[SUCCESS] AI models ready.")

    # ------------------------------
    # 3. Prepare AI engines
    # ------------------------------
    def prepare_engines(self):
        print("[INFO] Preparing AI engines...")
        # Example placeholders; extend with your full engine logic
        engines = ["image_gen", "video_gen", "audio_gen"]
        for eng in engines:
            print(f"[INFO] Engine '{eng}' is online (placeholder).")
        print("[SUCCESS] All engines online.")

    # ------------------------------
    # 4. Cloud Mentor integration
    # ------------------------------
    def cloud_mentor_integration(self):
        if self.enable_cloud_mentor:
            print("[INFO] Cloud Mentor activated.")
            # Placeholder: download/init cloud mentor configs
            cloud_config = os.path.join(self.caleb_core, "cloud_mentor")
            os.makedirs(cloud_config, exist_ok=True)
            print("[SUCCESS] Cloud Mentor ready.")

    # ------------------------------
    # 5. Run build pipeline
    # ------------------------------
    def run_build_pipeline(self):
        print("[INFO] Starting Caleb build pipeline...")
        self.setup_directories()
        self.install_models()
        self.prepare_engines()
        self.cloud_mentor_integration()
        print("[SUCCESS] Caleb has prepared Jack Hole Jackery Studio core environment!")

    # ------------------------------
    # 6. Entry point
    # ------------------------------
if __name__ == "__main__":
    enable_cloud = input("Enable Cloud Mentor? (y/N): ").strip().lower() == "y"
    builder = CalebBuilder(enable_cloud_mentor=enable_cloud)
    builder.run_build_pipeline()
