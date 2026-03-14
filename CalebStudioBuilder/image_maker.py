import torch
import time
from diffusers import StableDiffusionXLPipeline, StableDiffusionPipeline

class CalebImageMaker:
    def __init__(self):
        print("[SYS] Waking up Caleb's visual brain...")
        self.device = "xpu" if hasattr(torch, "xpu") and torch.xpu.is_available() else "cpu"
        self.pipeline = None
        self.current_model = None

    def load_model(self, model_choice):
        # Don't reload if it is already loaded
        if self.current_model == model_choice and self.pipeline is not None:
            return

        print(f"[SYS] Loading Art Model: {model_choice} into {self.device.upper()} VRAM...")
        
        # Free up VRAM before loading new model
        if self.pipeline is not None:
            del self.pipeline
            if self.device == "xpu":
                torch.xpu.empty_cache()

        try:
            if "SDXL" in model_choice:
                # Load SDXL
                self.pipeline = StableDiffusionXLPipeline.from_pretrained(
                    "stabilityai/stable-diffusion-xl-base-1.0", 
                    torch_dtype=torch.float16, 
                    variant="fp16", 
                    use_safetensors=True
                )
            else:
                # Fallback to standard SD 1.5
                self.pipeline = StableDiffusionPipeline.from_pretrained(
                    "runwayml/stable-diffusion-v1-5", 
                    torch_dtype=torch.float16
                )
                
            self.pipeline.to(self.device)
            self.current_model = model_choice
            print("[SYS] Visual brain fully loaded and ready.")
            
        except Exception as e:
            print(f"[!] Engine Misfire: Could not load {model_choice}. Error: {e}")
            self.pipeline = None

    def draw_advanced(self, prompt, filename="output.png", options=None):
        if options is None:
            options = {}
            
        model_choice = options.get("model", "SDXL Base 1.0")
        self.load_model(model_choice)
        
        if not self.pipeline:
            print("[!] Cannot draw. Pipeline is dead.")
            return False

        # Pull surgical controls from the UI dictionary
        steps = options.get("steps", 25)
        cfg = options.get("cfg", 7.0)
        neg_prompt = options.get("negative_prompt", "")
        seed_val = options.get("seed", 0)
        
        print(f"[FORGING] Prompt: {prompt}")
        print(f"[FORGING] Steps: {steps} | CFG: {cfg} | Seed: {seed_val}")
        
        # Handle the random seed
        if seed_val == 0:
            generator = None # Let it be random
        else:
            generator = torch.Generator(device=self.device).manual_seed(seed_val)

        try:
            # Generate the image
            image = self.pipeline(
                prompt=prompt,
                negative_prompt=neg_prompt,
                num_inference_steps=steps,
                guidance_scale=cfg,
                generator=generator
            ).images[0]
            
            image.save(filename)
            print(f"[SUCCESS] Image forged and saved as: {filename}")
            return True
            
        except Exception as e:
            print(f"[!] Forge Error: {e}")
            return False
