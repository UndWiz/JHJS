"""
model_manager.py
----------------
Handles loading, registering, and switching AI models for Caleb.

Capabilities:
- Multi-model orchestration (image, video, LLM, TTS)
- Dynamic loading of local and cloud models
- Shared memory registration for context continuity
- Specialized doppelgangers for different tasks
"""

import os
from pathlib import Path
from typing import Dict, Optional

# Import ML frameworks
try:
    import torch
    from diffusers import StableDiffusionPipeline
except ImportError:
    torch = None
    StableDiffusionPipeline = None

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
except ImportError:
    AutoModelForCausalLM = None
    AutoTokenizer = None

# Placeholder for shared memory registration
shared_memory: Dict[str, dict] = {}

class ModelManager:
    """
    Handles all AI model orchestration for Caleb.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.models: Dict[str, object] = {}  # Holds model objects
        self.model_paths: Dict[str, str] = {}  # Holds model paths
        self.active_model: Optional[str] = None
        self.model_path = Path(model_path) if model_path else Path("./models")
        self.model_path.mkdir(exist_ok=True)
        print(f"[ModelManager] Initialized. Model path: {self.model_path.resolve()}")

    def load_sd_model(self, model_name: str, local_path: Optional[str] = None):
        """Load a Stable Diffusion model (local or cloud)."""
        path = local_path or str(self.model_path / model_name)
        print(f"[ModelManager] Loading SD model '{model_name}' from {path}")
        if StableDiffusionPipeline is None:
            raise ImportError("diffusers not installed")
        model = StableDiffusionPipeline.from_pretrained(path)
        self.models[model_name] = model
        self.model_paths[model_name] = path
        self.register_in_memory(model_name, "image")
        print(f"[ModelManager] SD model '{model_name}' loaded successfully.")

    def load_llm_model(self, model_name: str, local_path: Optional[str] = None):
        """Load a language model (local or cloud)."""
        path = local_path or str(self.model_path / model_name)
        print(f"[ModelManager] Loading LLM '{model_name}' from {path}")
        if AutoModelForCausalLM is None:
            raise ImportError("transformers not installed")
        tokenizer = AutoTokenizer.from_pretrained(path)
        model = AutoModelForCausalLM.from_pretrained(path)
        self.models[model_name] = {"model": model, "tokenizer": tokenizer}
        self.model_paths[model_name] = path
        self.register_in_memory(model_name, "llm")
        print(f"[ModelManager] LLM '{model_name}' loaded successfully.")

    def switch_model(self, model_name: str):
        """Switch the active model."""
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' is not loaded")
        self.active_model = model_name
        print(f"[ModelManager] Active model switched to '{model_name}'")

    def get_active_model(self):
        """Return the currently active model object."""
        if self.active_model is None:
            raise ValueError("No active model selected")
        return self.models[self.active_model]

    def register_in_memory(self, model_name: str, model_type: str):
        """Register the model in shared memory for all agents."""
        shared_memory[model_name] = {"type": model_type, "path": self.model_paths[model_name]}
        print(f"[ModelManager] Model '{model_name}' registered in shared memory as '{model_type}'")

    def list_models(self):
        """List all loaded models."""
        return list(self.models.keys())

# Example usage (for testing only)
if __name__ == "__main__":
    mm = ModelManager()
    # mm.load_sd_model("stable-diffusion-1.5")   # Uncomment if local SD model exists
    # mm.load_llm_model("llama2-7b")             # Uncomment if local LLM exists
    print("[ModelManager] Loaded models:", mm.list_models())
