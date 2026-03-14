import os
import time
import asyncio
import edge_tts

class CalebAudioMaker:
    def __init__(self):
        print("[SYS] Audio lab is online.")
        # We set up a few professional sounding actors
        self.voices = {
            "Standard Male": "en-US-ChristopherNeural",
            "Standard Female": "en-US-AriaNeural",
            "Robot / Synthesizer": "en-US-SteffanNeural" # Pitch shifted later if needed
        }

    async def _generate(self, text, voice, filename):
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filename)

    def generate_voice(self, text, voice_type="Standard Male", filename="voiceover.mp3"):
        print(f"\n[AUDIO] Recording dialogue: '{text[:30]}...'")
        start = time.time()
        
        voice_id = self.voices.get(voice_type, "en-US-ChristopherNeural")
        
        # Run the async generation
        asyncio.run(self._generate(text, voice_id, filename))
        
        print(f"[SUCCESS] Audio saved to {filename} in {time.time() - start:.2f} seconds.")

if __name__ == "__main__":
    maker = CalebAudioMaker()
    maker.generate_voice("Welcome to Jack Hole Jackery Studios.", "Standard Male", "test_audio.mp3")
