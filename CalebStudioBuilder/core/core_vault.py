import os
import time
import json
import chromadb

class CalebVault:
    def __init__(self):
        self.base_path = os.path.expanduser("~/CalebStudioBuilder/projects")
        os.makedirs(self.base_path, exist_ok=True)
        
        # Init ChromaDB for Character DNA
        try:
            self.chroma_client = chromadb.PersistentClient(path=os.path.join(self.base_path, ".dna_vault"))
            self.dna_collection = self.chroma_client.get_or_create_collection(name="character_dna")
            print("[SYS] DNA Vault Online.")
        except Exception as e:
            print(f"[!] DNA Vault Error: {e}")
            self.chroma_client = None

    def create_project(self, name):
        p_path = os.path.join(self.base_path, name)
        folders = ["images", "video", "audio", "scripts", "temp"]
        for f in folders:
            os.makedirs(os.path.join(p_path, f), exist_ok=True)
            
        meta = {
            "name": name, 
            "created": time.ctime(), 
            "style": "Cartoon Mayhem",
            "active_characters": []
        }
        
        with open(os.path.join(p_path, "metadata.json"), "w") as f:
            json.dump(meta, f, indent=4)
            
        return p_path

    def save_character_dna(self, char_id, prompt_data):
        if self.chroma_client:
            self.dna_collection.add(
                documents=[prompt_data],
                metadatas=[{"type": "character", "timestamp": time.time()}],
                ids=[char_id]
            )
            return True
        return False
