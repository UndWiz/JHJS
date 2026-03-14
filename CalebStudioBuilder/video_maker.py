import os
import time
import subprocess

class CalebVideoMaker:
    def __init__(self):
        print("[SYS] Video VFX lab is online. (Using FFmpeg Motion Math)")

    def generate_motion(self, image_path, motion_style, filename="scene_clip.mp4"):
        if not os.path.exists(image_path):
            print(f"[!] Error: Cannot find image file {image_path}")
            return False

        print(f"\n[VIDEO] Applying '{motion_style}' to {image_path}...")
        start = time.time()

        # The Hollywood Math for the animations (5 second clips, 30fps)
        if motion_style == "Slow Cinematic Zoom":
            # Zooms into the center slowly
            vfx = "zoompan=z='min(zoom+0.0015,1.5)':d=150:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',framerate=30"
        elif motion_style == "Pan Right":
            # Zooms in slightly, then pans across the image to the right
            vfx = "zoompan=z=1.2:x='x+1':y='ih/2-(ih/zoom/2)':d=150,framerate=30"
        elif motion_style == "Pan Left":
            # Zooms in slightly, starts on the right, pans left
            vfx = "zoompan=z=1.2:x='if(eq(x,0),iw,x-1)':y='ih/2-(ih/zoom/2)':d=150,framerate=30"
        else:
            vfx = "zoompan=z='min(zoom+0.0015,1.5)':d=150,framerate=30"

        # The terminal command to build the MP4
        cmd = [
            "ffmpeg", "-y", "-i", image_path, 
            "-vf", vfx, 
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-t", "5", "-s", "896x512",
            filename
        ]

        try:
            # We run it quietly so it doesn't flood your terminal
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print(f"[SUCCESS] Video saved to {filename} in {time.time() - start:.2f} seconds.")
            return True
        except Exception as e:
            print(f"[!] Video rendering failed: {e}")
            return False

if __name__ == "__main__":
    # Test script - expects a file named 'test.png' to exist
    maker = CalebVideoMaker()
    # maker.generate_motion("test.png", "Slow Cinematic Zoom", "test_zoom.mp4")
