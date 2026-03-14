import os

class FileUtilities:
    """General static file helpers for path resolution and validation."""
    @staticmethod
    def ensure_dir(path):
        os.makedirs(path, exist_ok=True)
        
    @staticmethod
    def get_extension(filepath):
        return os.path.splitext(filepath)[1]

if __name__ == "__main__":
    print("[+] File Utilities initialized.")
