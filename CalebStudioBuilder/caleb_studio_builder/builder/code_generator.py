import requests
import json
import re

class CodeGenerator:
    def __init__(self):
        self.endpoint = "http://127.0.0.1:11434/api/generate"
        self.default_model = "qwen2.5-coder:7b"
        self.routing_map = {
            "python_generation": "qwen2.5-coder:7b",
            "filesystem_ops": "qwen2.5-coder:7b",
            "planning": "qwen2.5-coder:7b"
        }
        self.system_prompt = (
            "You are CALEB, a methodical senior software engineer local AI. "
            "You must use the provided XML tool schema to execute tasks. "
            "Deliver large structural work in minimal responses. "
            "Available tools: <write_file path='...'>, <patch_file path='...' line_start='...' line_end='...'>, "
            "<run_command>, <read_file>, <ask_user>."
        )

    def _determine_route(self, prompt, hybrid_enabled):
        if not hybrid_enabled:
            return self.default_model
            
        prompt_lower = prompt.lower()
        if "plan" in prompt_lower or "architect" in prompt_lower:
            return self.routing_map["planning"]
        elif "folder" in prompt_lower or "move" in prompt_lower or "delete" in prompt_lower:
            return self.routing_map["filesystem_ops"]
        else:
            return self.routing_map["python_generation"]

    def generate_response(self, user_prompt, context=None, hybrid_enabled=False):
        target_model = self._determine_route(user_prompt, hybrid_enabled)
        
        payload = {
            "model": target_model,
            "prompt": f"{self.system_prompt}\n\nUser Request: {user_prompt}",
            "stream": False,
            "options": {
                "num_predict": 16384,
                "temperature": 0.2
            }
        }
        
        if context: payload["context"] = context
            
        try:
            response = requests.post(self.endpoint, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result.get("response", ""), result.get("context", []), target_model
        except requests.exceptions.RequestException as e:
            return f"<ask_user>Local inference failed: {str(e)}</ask_user>", [], target_model

    def parse_tools(self, ai_response):
        commands = []
        write_pattern = re.compile(r"<write_file\s+path=['\"](.*?)['\"]>(.*?)</write_file>", re.DOTALL)
        patch_pattern = re.compile(r"<patch_file\s+path=['\"](.*?)['\"]\s+line_start=['\"](\d+)['\"]\s+line_end=['\"](\d+)['\"]>(.*?)</patch_file>", re.DOTALL)
        run_pattern = re.compile(r"<run_command>(.*?)</run_command>", re.DOTALL)
        
        for match in write_pattern.finditer(ai_response):
            commands.append({"tool": "write_file", "path": match.group(1), "content": match.group(2).strip()})
        for match in patch_pattern.finditer(ai_response):
            commands.append({
                "tool": "patch_file", "path": match.group(1), 
                "line_start": int(match.group(2)), "line_end": int(match.group(3)),
                "content": match.group(4).strip()
            })
        for match in run_pattern.finditer(ai_response):
            commands.append({"tool": "run_command", "cmd": match.group(1).strip()})
            
        return commands
