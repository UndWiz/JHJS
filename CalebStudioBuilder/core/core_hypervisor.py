import os
import time
import psutil
import sys

try:
    import torch
except ImportError:
    pass

# Muzzle the broken Intel version check
try:
    import intel_extension_for_pytorch as ipex
except Exception as e:
    pass

class CalebHypervisor:
    def __init__(self):
        self.active_engine = "CALEB Core"
        self.vram_limit_gb = 13.0 # Danger zone for 16GB Arc A770
        print("[SYS] CALEB Hypervisor Online. Guarding VRAM.")

    def get_vram_usage(self):
        try:
            if hasattr(torch, "xpu") and torch.xpu.is_available():
                return torch.xpu.memory_allocated() / (1024**3)
        except Exception:
            pass
        return 0.0

    def hibernate_all(self):
        print("[HYPERVISOR] Hibernating engines... clearing Arc XPU cache.")
        try:
            if hasattr(torch, "xpu") and torch.xpu.is_available():
                torch.xpu.empty_cache()
        except Exception:
            pass
        self.active_engine = "None (Hibernating)"

    def wake_engine(self, engine_name):
        if self.active_engine == engine_name:
            return 
            
        print(f"[HYPERVISOR] Requesting wake for: {engine_name}")
        
        if self.get_vram_usage() > self.vram_limit_gb:
            print(f"[HYPERVISOR] VRAM bottleneck detected. Forcing hibernation.")
            self.hibernate_all()
            
        self.active_engine = engine_name
        print(f"[HYPERVISOR] {engine_name} is now loaded in Arc GPU.")
