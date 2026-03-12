import os
import shutil
import difflib
from datetime import datetime

class FileManager:
    def __init__(self, project_root):
        self.project_root = os.path.abspath(project_root)

    def _secure_path(self, relative_path):
        target = os.path.abspath(os.path.join(self.project_root, relative_path))
        if not target.startswith(self.project_root):
            raise PermissionError(f"[SECURITY LOCKOUT] Path traversal blocked: {relative_path}")
        return target

    def _backup_file(self, filepath):
        if os.path.exists(filepath):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{filepath}.{timestamp}.bak"
            shutil.copy2(filepath, backup_path)
            return backup_path
        return None

    def read_file(self, path):
        target = self._secure_path(path)
        if not os.path.exists(target):
            return ""
        with open(target, 'r', encoding='utf-8') as f:
            return f.read()

    def generate_diff(self, original_text, new_text, filename):
        """Generates a unified diff for preview mode."""
        diff = difflib.unified_diff(
            original_text.splitlines(keepends=True),
            new_text.splitlines(keepends=True),
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}"
        )
        return "".join(diff)

    def write_file(self, path, content, preview=False):
        target = self._secure_path(path)
        original = self.read_file(path)
        
        if preview:
            return self.generate_diff(original, content, os.path.basename(path))
            
        os.makedirs(os.path.dirname(target), exist_ok=True)
        self._backup_file(target)
        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)
        if target.endswith('.py') or target.endswith('.sh'):
            os.chmod(target, 0o755)
        return "File written successfully."

    def patch_file(self, path, line_start, line_end, content, preview=False):
        target = self._secure_path(path)
        original_lines = []
        if os.path.exists(target):
            with open(target, 'r', encoding='utf-8') as f:
                original_lines = f.readlines()
                
        start_idx = max(0, int(line_start) - 1)
        end_idx = min(len(original_lines), int(line_end))
        
        new_lines = [line + '\n' for line in content.split('\n')]
        if new_lines and new_lines[-1] == '\n':
            new_lines.pop()
            
        patched_lines = original_lines[:start_idx] + new_lines + original_lines[end_idx:]
        
        if preview:
            return self.generate_diff("".join(original_lines), "".join(patched_lines), os.path.basename(path))
            
        self._backup_file(target)
        with open(target, 'w', encoding='utf-8') as f:
            f.writelines(patched_lines)
        return "File patched successfully."
