import torch
import time

print("--- CALEB BRAIN CHECK ---")
print(f"PyTorch Version: {torch.__version__}")
print(f"Arc GPU Awake: {torch.xpu.is_available()}")

if not torch.xpu.is_available():
    print("[!] GPU is still sleeping. We might need to check the install logs.")
    exit()

from diffusers import StableDiffusionPipeline

# This assumes your folder structure is the same as before
model_path = "/home/jhjs/CalebStudioBuilder/models/diffusion/v1-5-pruned-emaonly.safetensors"
print(f"\n[SYS] Loading: {model_path}")

# Send it straight to the Intel card
pipe = StableDiffusionPipeline.from_single_file(model_path, torch_dtype=torch.float16)
pipe = pipe.to("xpu")

prompt = "a futuristic cyberpunk neon coffee mug sitting on a desk, highly detailed, 8k"
print(f"[SYS] Drawing: '{prompt}'")

start = time.time()
image = pipe(prompt, num_inference_steps=20).images[0]
image.save("success_mug.png")

print(f"\n[SUCCESS] You did it man! Image saved in {time.time() - start:.2f} seconds!")
