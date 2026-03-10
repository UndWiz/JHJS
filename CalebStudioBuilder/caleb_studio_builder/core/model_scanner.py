import glob
import os
import requests

class ModelScanner:
    def __init__(self, models_dir="models"):
        self.models_dir = os.path.abspath(models_dir)
        self.ollama_endpoint = "http://127.0.0.1:11434/api/tags"

    def scan_local_gguf(self):
        """Detects raw GGUF models in the local directory."""
        if not os.path.exists(self.models_dir):
            return []
        return [os.path.basename(f) for f in glob.glob(os.path.join(self.models_dir, "*.gguf"))]

    def scan_ollama(self):
        """Queries local Ollama instance for available engines."""
        try:
            response = requests.get(self.ollama_endpoint, timeout=3)
            if response.status_code == 200:
                return [model["name"] for model in response.json().get("models", [])]
        except requests.exceptions.RequestException:
            pass
        return []

    def get_all_active_engines(self):
        return {
            "gguf": self.scan_local_gguf(),
            "ollama": self.scan_ollama()
        }

if __name__ == "__main__":
    scanner = ModelScanner(os.path.join(os.getcwd(), "caleb_studio_builder", "models"))
    print(f"Available Engines: {scanner.get_all_active_engines()}")
