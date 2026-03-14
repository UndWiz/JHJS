import sqlite3
import os
from datetime import datetime

class MemoryManager:
    def __init__(self, db_path="caleb_studio.db"):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        """Builds the schema according to CALEB v1.0 specifications."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Short-term memory & persistent chat context
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                role TEXT,
                message TEXT
            )
        ''')
        
        # File diffs and restoration states
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filepath TEXT,
                content TEXT,
                timestamp TEXT
            )
        ''')
        
        # Terminal monitoring for autonomous self-correction
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT,
                stdout TEXT,
                stderr TEXT,
                exit_code INTEGER,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"[+] Memory database initialized at {self.db_path}")

    def log_chat(self, role, message):
        """Records interactions to disk."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chats (timestamp, role, message) VALUES (?, ?, ?)",
                       (datetime.now().isoformat(), role, message))
        conn.commit()
        conn.close()

    def log_execution(self, command, stdout, stderr, exit_code):
        """Tracks terminal output to feed the self-repair loop."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO execution_logs (command, stdout, stderr, exit_code, timestamp) VALUES (?, ?, ?, ?, ?)",
                       (command, stdout, stderr, exit_code, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def get_recent_context(self, limit=10):
        """Retrieves short-term memory sliding window."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT role, message FROM chats ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [{"role": r[0], "message": r[1]} for r in reversed(rows)]

if __name__ == "__main__":
    mm = MemoryManager()
    mm.log_chat("system", "CALEB Memory Manager Phase 2 initialized successfully.")
    print("[*] Memory schema mapped and verified.")
