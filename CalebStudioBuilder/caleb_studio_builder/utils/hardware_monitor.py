import psutil
import subprocess
import os

class HardwareMonitor:
    def __init__(self, vram_total_gb=16.0):
        self.vram_total_gb = vram_total_gb
        # Initialize CPU percent baseline
        psutil.cpu_percent(interval=None)

    def get_stats(self):
        """Retrieves real-time system metrics."""
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()
        ram_used_gb = ram.used / (1024**3)
        ram_total_gb = ram.total / (1024**3)
        
        # Intel Arc A770 VRAM estimation (fallback if specific intel_gpu_top parsing isn't configured)
        vram_used_gb = self._get_vram_usage()

        return {
            "cpu": cpu,
            "ram_used": round(ram_used_gb, 1),
            "ram_total": round(ram_total_gb, 1),
            "vram_used": round(vram_used_gb, 1),
            "vram_total": self.vram_total_gb
        }

    def _get_vram_usage(self):
        """
        Attempts to read GPU VRAM. 
        For Intel Arc on Linux, this typically requires specific sysfs parsing or tools.
        Defaulting to a safe proxy metric or 0.0 if inaccessible without sudo.
        """
        try:
            # Check for standard memory sysfs paths for drm/card0
            mem_path = "/sys/class/drm/card0/device/mem_info_vram_used"
            if os.path.exists(mem_path):
                with open(mem_path, 'r') as f:
                    bytes_used = int(f.read().strip())
                    return bytes_used / (1024**3)
            return 0.0
        except Exception:
            return 0.0

if __name__ == "__main__":
    monitor = HardwareMonitor()
    print(f"Hardware Stats: {monitor.get_stats()}")
