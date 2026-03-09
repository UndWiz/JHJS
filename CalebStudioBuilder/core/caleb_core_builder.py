# caleb_core_builder.py
import os
import sys
import json
import subprocess
from pathlib import Path
from file_manager import FileManager
from memory_manager import MemoryManager
from dependency_manager import DependencyManager

class CalebCoreBuilder:
    """
    Core engine for CalebStudioBuilder.
    Handles project directories, model downloads, and file setup.
    """

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.home() / "CalebStudio"
        self.memory = MemoryManager(self.base_path / "caleb_memory.json")
        self.file_manager = FileManager(self.base_path)
        self.dependency_manager = DependencyManager()

        # Define default structure for CalebStudioBuilder
        self.structure = {
            "models": ["image_models", "video_models", "audio_models", "llm_models"],
            "scripts": ["tasks", "automation", "training"],
            "assets": ["images", "audio", "3d"],
            "config": [],
            "logs": [],
            "output": ["renders", "videos", "audio_output"]
        }

        # Default model URLs (free / open sources)
        self.model_sources = {
            "image_models": {
                "sdxl_base": "https://huggingface.co/stabilityai/sdxl-base/resolve/main/model.safetensors",
                "sdxl_refiner": "https://huggingface.co/stabilityai/sdxl-refiner/resolve/main/model.safetensors"
            },
            "video_models": {},
            "audio_models": {},
            "llm_models": {}
        }

    def setup_directories(self):
        """Create all project directories."""
        print(f"[CalebBuilder] Setting up project directories at {self.base_path}")
        for main_dir, subdirs in self.structure.items():
            dir_path = self.base_path / main_dir
            self.file_manager.create_dir(dir_path)
            for sub in subdirs:
                self.file_manager.create_dir(dir_path / sub)

    def check_dependencies(self):
        """Ensure required Python packages are installed."""
        print("[CalebBuilder] Checking dependencies...")
        required_packages = ["torch", "diffusers", "transformers", "onnxruntime", "accelerate", "chromadb", "requests", "tqdm"]
        self.dependency_manager.install_packages(required_packages)

    def download_models(self):
        """Download models if they do not exist."""
        print("[CalebBuilder] Checking and downloading models...")
        for category, models in self.model_sources.items():
            target_dir = self.base_path / "models" / category
            self.file_manager.create_dir(target_dir)
            for name, url in models.items():
                file_path = target_dir / f"{name}.safetensors"
                if not file_path.exists():
                    print(f"Downloading {name} from {url}...")
                    self.download_file(url, file_path)
                    self.memory.record_model_download(name, str(file_path))
                else:
                    print(f"{name} already exists, skipping.")

    def download_file(self, url: str, target_path: Path):
        """Download a file from URL with progress."""
        import requests
        from tqdm import tqdm

        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        with open(target_path, 'wb') as f, tqdm(
            desc=target_path.name,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                bar.update(size)

    def run(self):
        """Main execution method."""
        print("[CalebBuilder] Starting CalebStudioBuilder setup...")
        self.check_dependencies()
        self.setup_directories()
        self.download_models()
        print("[CalebBuilder] Setup complete! CalebStudioBuilder is ready.")

if __name__ == "__main__":
    builder = CalebCoreBuilder()
    builder.run()
