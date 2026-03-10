import subprocess
import sys

class DependencyInstaller:
    """Handles autonomous package resolution and installation with retry logic."""
    def __init__(self, max_retries=3):
        self.max_retries = max_retries

    def install(self, package_name):
        attempts = 0
        while attempts < self.max_retries:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package_name],
                    capture_output=True, text=True, check=True
                )
                return True, result.stdout
            except subprocess.CalledProcessError as e:
                attempts += 1
                if attempts >= self.max_retries:
                    return False, f"Failed to install {package_name} after {self.max_retries} attempts: {e.stderr}"
        return False, "Unknown Error"

if __name__ == "__main__":
    installer = DependencyInstaller()
    print("[+] Dependency Installer Module initialized.")
