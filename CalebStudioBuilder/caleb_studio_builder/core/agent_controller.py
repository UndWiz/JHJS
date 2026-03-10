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
            
        return self._execution_loop(user_text, log_callback, attempt=1, current_role="coder")

    def _execution_loop(self, prompt, log_callback, attempt=1, current_role="coder"):
        context = self.memory.get_recent_context(limit=10)
        formatted_context = "\n".join([f"{msg['role']}: {msg['message']}" for msg in context])
        
        ai_raw, _, model_used = self.ai.generate_response(prompt, context=formatted_context, hybrid_enabled=self.hybrid_mode, role=current_role)
        self.memory.log_chat("assistant", ai_raw)
        
        if log_callback: log_callback(f"[SYS] {current_role.capitalize()} Inference complete.")
        
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

            elif tool == "run_command":
                if self.sandbox_mode:
                    results.append(f"[SANDBOX BLOCKED] Command execution prevented: {cmd['cmd']}")
                    continue
                res = self.shell.execute(cmd["cmd"])
                self.memory.log_execution(cmd["cmd"], res["stdout"], res["stderr"], res["exit_code"])
                if res["exit_code"] == 0:
                    out_text = res["stdout"].strip()
                    if out_text:
                        results.append(f"[CMD SUCCESS]: {cmd['cmd']}\nOutput:\n{out_text}")
                    else:
                        results.append(f"[CMD SUCCESS]: {cmd['cmd']}")
                else:
                    error_msg = f"[CMD FAILED]: {cmd['cmd']}\nError: {res['stderr']}"
                    results.append(error_msg)
                    needs_repair = True
                    repair_prompt = f"The command `{cmd['cmd']}` failed. Error:\n{res['stderr']}\nFix the code and test again."

            elif tool == "load_template":
                template_path = os.path.join(self.project_root, "caleb_studio_builder", "templates", f"{cmd['name']}.py.tpl")
                if os.path.exists(template_path):
                    content = self.files.read_file(template_path)
                    # Inject the template directly into the agent's memory for the next thought cycle
                    self.memory.log_chat("system", f"TEMPLATE LOADED ({cmd['name']}):\n{content}\nNow use <write_file> to fill in the variables and save it.")
                    results.append(f"[TEMPLATE INJECTED] {cmd['name']} loaded into context. Issue command again to write.")
                else:
                    results.append(f"[TEMPLATE FAILED] {cmd['name']}.py.tpl not found.")

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
                    results.append(f"[PREVIEW DELETE] {cmd['path']}")

            elif tool == "read_file":
                content = self.files.read_file(cmd["path"])
                truncated = content[:2000] + "... [TRUNCATED]" if len(content) > 2000 else content
                self.memory.log_chat("system", f"Content of {cmd['path']}:\n{truncated}")
                results.append(f"[READ] {cmd['path']} (Loaded into memory)")

        # The Verifier Loop Upgrade
        if needs_repair and attempt <= 3:
            if log_callback: log_callback(f"[!] Engaging VERIFIER Agent. Self-Repair Loop (Attempt {attempt}/3)...")
            self.memory.log_chat("system", repair_prompt)
            # Recursively call execution loop, but forcefully swap the personality to "verifier"
            _, repair_results = self._execution_loop(repair_prompt, log_callback, attempt=attempt + 1, current_role="verifier")
            results.extend(repair_results)
        elif needs_repair and attempt > 3:
            if log_callback: log_callback("[!] Fatal: Verifier exhausted 3 attempts. Halting.")

        return ai_raw, results
