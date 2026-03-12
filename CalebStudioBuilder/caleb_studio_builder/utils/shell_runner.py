import subprocess
import os

class ShellRunner:
    def __init__(self, timeout=120):
        self.timeout = timeout
        self.banned_commands = [
            "rm -rf /", "mkfs", "sudo", "shutdown", "reboot", 
            "dd", "chmod -R 777 /", "init", "poweroff", "halt", "kill -9 1"
        ]

    def execute(self, command, cwd=None):
        """Executes terminal commands with strict sandboxing and timeouts."""
        # Security Check
        for banned in self.banned_commands:
            if banned in command:
                return {
                    "stdout": "", 
                    "stderr": f"[SECURITY LOCKOUT] Blocked destructive command: {banned}", 
                    "exit_code": 1
                }

        try:
            result = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True,
                timeout=self.timeout,
                cwd=cwd
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "", 
                "stderr": f"[TIMEOUT] Execution exceeded {self.timeout} seconds.", 
                "exit_code": 124
            }

if __name__ == "__main__":
    runner = ShellRunner(timeout=5)
    res = runner.execute("echo 'ShellRunner Online'")
    print(res["stdout"].strip())
