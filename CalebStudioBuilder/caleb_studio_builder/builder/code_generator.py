import os
import re
import textwrap
from llama_cpp import Llama

class CodeGenerator:
    def __init__(self):
        # We are using the local model we just downloaded
        model_path = os.path.expanduser("~/CalebStudioBuilder/models/llm/qwen2.5-coder-7b-instruct-q4_k_m.gguf")
        self.default_model = "qwen2.5-coder"
        
        # We wrap it in a try-except so if the file isn't there, the whole app doesn't crash on boot
        try:
            print(f"[SYS] Loading text brain from: {model_path}")
            # n_gpu_layers=-1 tells it to offload everything to the Arc GPU via Vulkan
            # n_ctx=4096 gives him enough memory so he doesn't hit a wall
            self.llm = Llama(
                model_path=model_path,
                n_gpu_layers=-1, 
                n_ctx=4096,
                verbose=False
            )
        except Exception as e:
            print(f"[!] Text brain failed to load: {e}")
            self.llm = None
        
        self.prompts = {
            "coder": (
                "You are CALEB, the lead AI brain of Jack Hole Jackery Studios. "
                "You can brainstorm ideas and have a regular conversation with the user to help make TV shows, games, and art. "
                "Use normal simple talking. Don't use overly educated sounding speech. "
                "If the user specifically asks you to write code, create files, or run terminal commands, THEN use your XML tools like <write_file path=''>...</write_file>. "
                "Otherwise, just talk normal and act like a helpful studio partner."
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
        if not self.llm:
             return "<ask_user>My text brain isn't loaded. Check the terminal for errors.</ask_user>", [], "None"

        if role == "coder" and ("plan" in user_prompt.lower() or "architect" in user_prompt.lower()):
            role = "planner"
            
        system_prompt = self.prompts.get(role, self.prompts["coder"])
        
        # Llama-cpp uses a specific list format for chat memory
        messages = [{"role": "system", "content": system_prompt}]
        
        if context:
            # We shove the context history in as a "user" message so he remembers it
            messages.append({"role": "user", "content": f"Chat History:\n{context}"})
            
        messages.append({"role": "user", "content": f"User Request: {user_prompt}"})
        
        try:
            # Fire the local engine with the fixed max_tokens so he doesn't run out of breath
            response = self.llm.create_chat_completion(
                messages=messages,
                temperature=0.2,
                max_tokens=1024
            )
            # Rip the actual text answer out of the dictionary it returns
            result_text = response["choices"][0]["message"]["content"]
            return result_text, [], self.default_model
        except Exception as e:
            return f"<ask_user>Local inference failed: {str(e)}</ask_user>", [], self.default_model

    def _clean_markdown(self, text):
        # Strict extraction: If backticks exist, rip out ONLY what is inside them
        match = re.search(r"```[a-zA-Z]*\n(.*?)```", text, re.DOTALL)
        code = match.group(1) if match else text
        # textwrap.dedent mathematically strips out the fake XML padding spaces
        return textwrap.dedent(code).strip('\n')

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
