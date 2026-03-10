import logging
import os
from datetime import datetime

class CalebLogger:
    """Standardized logging utility for background CALEB processes."""
    def __init__(self, log_dir="caleb_memory/logs"):
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d')
        self.log_file = os.path.join(log_dir, f"caleb_system_{timestamp}.log")
        
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def info(self, msg): logging.info(msg)
    def warning(self, msg): logging.warning(msg)
    def error(self, msg): logging.error(msg)

if __name__ == "__main__":
    print("[+] System Logger initialized.")
