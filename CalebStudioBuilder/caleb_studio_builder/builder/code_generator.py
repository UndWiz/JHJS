import requests
import json
import re

class CodeGenerator:
    def __init__(self):
        self.endpoint = "http://" + "127.0.0.1:11434" + "/api/generate"
        self.default_model = "qwen2.5-coder:7b"
        
        self.prompts = {
            "coder": (
                "You are CALEB, an autonomous Coder Agent. You MUST use XML tags to act. "
                "Tools: <create_folder>, <write_file path=''>, <run_command>, <patch_file>, <read_file>, <load_template name=''>. "
                "Never give conversational text. Format your entire response as a sequence of tools. "
                "To use a template: <load_template name='cli_script'></load_template>"
            ),
            "verifier": (
                "You are CALEB, a Debugging Verifier Agent. "
                "The previous command FAILED. Review the terminal error in the Chat History. "
                "Use <patch_file> or <write_file> to fix the error, then use <run_command> to test it again. "
                "You MUST use XML tools. Do not explain the fix, just execute it."
            ),
            "planner": (
                "You are CALEB, an Architect Agent. "
                "Break down the user's request into a technical, step-by-step plan. "
                "Do NOT write code. Output a numbered list of exactly which files need to be created and which tools the Coder should use next."
            )
        }

    def generate_response(self, user_prompt, context=None, hybrid_enabled=False, role="coder"):
        if role == "coder" and ("plan" in user_prompt.lower() or "architect" in user_prompt.lower()):
            role = "planner"
            
        system_prompt = self.prompts.get(role, self.prompts["coder"])
        
        full_prompt = f"{system_prompt}\n\nChat History:\n{context}\n\nUser Request: {user_prompt}" if context else f"{system_prompt}\n\nUser Request: {user_prompt}"
        
        payload = {
            "model": self.default_model,
            "prompt": full_prompt,
            "stream": False,
            "options": {"num_ctx": 8192, "temperature": 0.2}
        }
        
        try:
            response = requests.post(self.endpoint, json=payload, timeout=120)
            if response.status_code != 200:
                return f"<ask_user>Ollama API Error {response.status_code}: {response.text}</ask_user>", [], self.default_model
            response.raise_for_status()
            result = response.json()
            return result.get("response", ""), [], self.default_model
        except Exception as e:
            return f"<ask_user>Local inference failed: {str(e)}</ask_user>", [], self.default_model

    def _clean_markdown(self, text):
        text = text.strip()
        lines = text.split('\n')
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        return '\n'.join(lines)

    def parse_tools(self, ai_response):
        commands = []
        for m in re.finditer(r"<write_file\s+path=['\"](.*?)['\"]>(.*?)</write_file>", ai_response, re.DOTALL):
            commands.append({"tool": "write_file", "path": m.group(1), "content": self._clean_markdown(m.group(2))})
        for m in re.finditer(r"<patch_file\s+path=['\"](.*?)['\"]\s+line_start=['\"](\d+)['\"]\s+line_end=['\"](\d+)['\"]>(.*?)</patch_file>", ai_response, re.DOTALL):
            commands.append({"tool": "patch_file", "path": m.group(1), "line_start": int(m.group(2)), "line_end": int(m.group(3)), "content": self._clean_markdown(m.group(4))})
        for m in re.finditer(r"<append_file\s+path=['\"](.*?)['\"]>(.*?)</append_file>", ai_response, re.DOTALL):
            commands.append({"tool": "append_file", "path": m.group(1), "content": self._clean_markdown(m.group(2))})
        for m in re.finditer(r"<run_command>(.*?)</run_command>", ai_response, re.DOTALL):
            commands.append({"tool": "run_command", "cmd": m.group(1).strip()})
        for m in re.finditer(r"<create_folder>(.*?)</create_folder>", ai_response, re.DOTALL):
            commands.append({"tool": "create_folder", "path": m.group(1).strip()})
        for m in re.finditer(r"<delete_file>(.*?)</delete_file>", ai_response, re.DOTALL):
            commands.append({"tool": "delete_file", "path": m.group(1).strip()})
        for m in re.finditer(r"<read_file>(.*?)</read_file>", ai_response, re.DOTALL):
            commands.append({"tool": "read_file", "path": m.group(1).strip()})
        for m in re.finditer(r"<list_dir>(.*?)</list_dir>", ai_response, re.DOTALL):
            commands.append({"tool": "list_dir", "path": m.group(1).strip()})
        for m in re.finditer(r"<search_codebase\s+pattern=['\"](.*?)['\"]>(.*?)</search_codebase>", ai_response, re.DOTALL):
            commands.append({"tool": "search_codebase", "pattern": m.group(1), "path": m.group(2).strip()})
        for m in re.finditer(r"<ask_user>(.*?)</ask_user>", ai_response, re.DOTALL):
            commands.append({"tool": "ask_user", "question": m.group(1).strip()})
        for m in re.finditer(r"<load_template\s+name=['\"](.*?)['\"]\s*>.*?</load_template>", ai_response, re.DOTALL):
            commands.append({"tool": "load_template", "name": m.group(1).strip()})
        for m in re.finditer(r"<load_template\s+name=['\"](.*?)['\"]\s*/>", ai_response, re.DOTALL):
            commands.append({"tool": "load_template", "name": m.group(1).strip()})
        return commands
