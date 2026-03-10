import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from caleb_studio_builder.core.memory_manager import MemoryManager
from caleb_studio_builder.core.file_manager import FileManager
from caleb_studio_builder.utils.shell_runner import ShellRunner
from caleb_studio_builder.builder.code_generator import CodeGenerator
from caleb_studio_builder.core.code_indexer import CodeIndexer
from caleb_studio_builder.utils.hardware_monitor import HardwareMonitor

class AgentController:
    def __init__(self, project_root):
        self.project_root = project_root
        self.memory = MemoryManager()
        self.files = FileManager(project_root)
        self.shell = ShellRunner()
        self.ai = CodeGenerator()
        self.indexer = CodeIndexer(project_root)
        self.indexer.scan_project()
        self.hw_monitor = HardwareMonitor()
        self.hw_limits = {'vram_cap': 15, 'ram_limit': 14}
        
        self.preview_mode = False
        self.sandbox_mode = False
        self.hybrid_mode = False

    def update_config(self, config_dict):
        self.hybrid_mode = config_dict.get("ai", {}).get("hybrid_mode", False)
        self.hw_limits = config_dict.get("hardware", self.hw_limits)

    def set_modes(self, preview_mode, sandbox_mode):
        self.preview_mode = preview_mode
        self.sandbox_mode = sandbox_mode

    def _check_hardware_limits(self):
        stats = self.hw_monitor.get_stats()
        if stats['vram_used'] > self.hw_limits.get('vram_cap', 15):
            return False, f"VRAM Limit Exceeded ({stats['vram_used']}GB > {self.hw_limits.get('vram_cap')}GB). Aborting."
        if stats['ram_used'] > self.hw_limits.get('ram_limit', 14):
            return False, f"RAM Limit Exceeded ({stats['ram_used']}GB > {self.hw_limits.get('ram_limit')}GB). Aborting."
        return True, "Hardware within limits."

    def process_user_input(self, user_text, log_callback=None):
        self.memory.log_chat("user", user_text)
        if log_callback: log_callback(f"[USER] {user_text}")
        
        hw_ok, hw_msg = self._check_hardware_limits()
        if not hw_ok:
            if log_callback: log_callback(f"[SECURITY LOCKOUT] {hw_msg}")
            self.memory.log_chat("system", f"Execution blocked: {hw_msg}")
            return "", [hw_msg]
            
        return self._execution_loop(user_text, log_callback, attempt=1)

    def _execution_loop(self, prompt, log_callback, attempt=1):
        context = self.memory.get_recent_context(limit=10)
        formatted_context = "\n".join([f"{msg['role']}: {msg['message']}" for msg in context])
        
        ai_raw, _, model_used = self.ai.generate_response(prompt, context=formatted_context, hybrid_enabled=self.hybrid_mode)
        self.memory.log_chat("assistant", ai_raw)
        
        if log_callback: log_callback(f"[SYS] Inference complete. Engine used: {model_used}")
        
        commands = self.ai.parse_tools(ai_raw)
        results = []
        
        if not commands:
            return ai_raw, ["No actionable tools found."]

        needs_repair = False
        repair_prompt = ""

        for cmd in commands:
            tool = cmd.get("tool")
            if tool == "write_file":
                res = self.files.write_file(cmd["path"], cmd["content"], preview=self.preview_mode)
                prefix = "[PREVIEW]" if self.preview_mode else "[WROTE]"
                results.append(f"{prefix} {cmd['path']}: {res}")
                if not self.preview_mode: self.indexer.scan_project()
                
            elif tool == "patch_file":
                res = self.files.patch_file(cmd["path"], cmd["line_start"], cmd["line_end"], cmd["content"], preview=self.preview_mode)
                prefix = "[PREVIEW]" if self.preview_mode else "[PATCHED]"
                results.append(f"{prefix} {cmd['path']}: {res}")
                if not self.preview_mode: self.indexer.scan_project()

            elif tool == "append_file":
                if not self.preview_mode:
                    self.files.append_file(cmd["path"], "\n" + cmd["content"])
                    results.append(f"[APPENDED] {cmd['path']}")
                else:
                    results.append(f"[PREVIEW APPEND] {cmd['path']}")
                
            elif tool == "run_command":
                if self.sandbox_mode:
                    results.append(f"[SANDBOX BLOCKED] Command execution prevented: {cmd['cmd']}")
                    continue
                res = self.shell.execute(cmd["cmd"])
                self.memory.log_execution(cmd["cmd"], res["stdout"], res["stderr"], res["exit_code"])
                if res["exit_code"] == 0:
                    results.append(f"[CMD SUCCESS]: {cmd['cmd']}")
                else:
                    error_msg = f"[CMD FAILED]: {cmd['cmd']}\nError: {res['stderr']}"
                    results.append(error_msg)
                    needs_repair = True
                    repair_prompt = f"The command `{cmd['cmd']}` returned exit code {res['exit_code']} with stderr:\n{res['stderr']}\nFix the code using <patch_file> or <write_file> and run it again."

            elif tool == "create_folder":
                target = self.files._secure_path(cmd["path"])
                if not self.preview_mode:
                    os.makedirs(target, exist_ok=True)
                    results.append(f"[CREATED DIR] {cmd['path']}")
                else:
                    results.append(f"[PREVIEW DIR] {cmd['path']}")

            elif tool == "delete_file":
                target = self.files._secure_path(cmd["path"])
                if not self.preview_mode:
                    if os.path.exists(target):
                        os.remove(target)
                        results.append(f"[DELETED] {cmd['path']}")
                    else:
                        results.append(f"[DELETE FAILED] File not found: {cmd['path']}")
                else:
                    results.append(f"[PREVIEW DELETE] {cmd['path']}")

            elif tool == "read_file":
                content = self.files.read_file(cmd["path"])
                truncated = content[:2000] + "... [TRUNCATED]" if len(content) > 2000 else content
                self.memory.log_chat("system", f"Content of {cmd['path']}:\n{truncated}")
                results.append(f"[READ] {cmd['path']} (Loaded into context memory)")

            elif tool == "list_dir":
                target = self.files._secure_path(cmd["path"])
                try:
                    contents = os.listdir(target)
                    self.memory.log_chat("system", f"Directory {cmd['path']} contents:\n{', '.join(contents)}")
                    results.append(f"[LIST DIR] {cmd['path']} mapped to context.")
                except Exception as e:
                    results.append(f"[LIST FAILED] {cmd['path']}: {str(e)}")

            elif tool == "search_codebase":
                target = self.files._secure_path(cmd["path"])
                res = self.shell.execute(f"grep -rnw '{target}' -e '{cmd['pattern']}'")
                if res['exit_code'] == 0:
                    self.memory.log_chat("system", f"Search results for {cmd['pattern']}:\n{res['stdout'][:2000]}")
                    results.append(f"[SEARCH SUCCESS] Found '{cmd['pattern']}' in {cmd['path']}")
                else:
                    results.append(f"[SEARCH FAILED] Pattern '{cmd['pattern']}' not found.")

            elif tool == "ask_user":
                results.append(f"[AI QUESTION] {cmd['question']}")
                if log_callback: log_callback(f"[!] AI requires input: {cmd['question']}")

        if needs_repair and attempt <= 3:
            if log_callback: log_callback(f"[!] Warning: Execution failed. Initializing Self-Repair Loop (Attempt {attempt}/3)...")
            self.memory.log_chat("system", repair_prompt)
            _, repair_results = self._execution_loop(repair_prompt, log_callback, attempt=attempt + 1)
            results.extend(repair_results)
        elif needs_repair and attempt > 3:
            if log_callback: log_callback("[!] Fatal: Self-Repair exhausted maximum attempts (3). Halting execution sequence.")

        return ai_raw, results
