import re

with open("caleb_studio_builder/builder/code_generator.py", "r") as f:
    content = f.read()

new_parser = """    def parse_tools(self, ai_response):
        commands = []
        
        # Define regex patterns for all 10 CALEB tools
        patterns = {
            "write_file": re.compile(r"<write_file\s+path=['\"](.*?)['\"]>(.*?)</write_file>", re.DOTALL),
            "patch_file": re.compile(r"<patch_file\s+path=['\"](.*?)['\"]\s+line_start=['\"](\d+)['\"]\s+line_end=['\"](\d+)['\"]>(.*?)</patch_file>", re.DOTALL),
            "append_file": re.compile(r"<append_file\s+path=['\"](.*?)['\"]>(.*?)</append_file>", re.DOTALL),
            "run_command": re.compile(r"<run_command>(.*?)</run_command>", re.DOTALL),
            "create_folder": re.compile(r"<create_folder>(.*?)</create_folder>", re.DOTALL),
            "delete_file": re.compile(r"<delete_file>(.*?)</delete_file>", re.DOTALL),
            "read_file": re.compile(r"<read_file>(.*?)</read_file>", re.DOTALL),
            "list_dir": re.compile(r"<list_dir>(.*?)</list_dir>", re.DOTALL),
            "search_codebase": re.compile(r"<search_codebase\s+pattern=['\"](.*?)['\"]>(.*?)</search_codebase>", re.DOTALL),
            "ask_user": re.compile(r"<ask_user>(.*?)</ask_user>", re.DOTALL)
        }
        
        for match in patterns["write_file"].finditer(ai_response):
            commands.append({"tool": "write_file", "path": match.group(1), "content": match.group(2).strip()})
        for match in patterns["patch_file"].finditer(ai_response):
            commands.append({"tool": "patch_file", "path": match.group(1), "line_start": int(match.group(2)), "line_end": int(match.group(3)), "content": match.group(4).strip()})
        for match in patterns["append_file"].finditer(ai_response):
            commands.append({"tool": "append_file", "path": match.group(1), "content": match.group(2).strip()})
        for match in patterns["run_command"].finditer(ai_response):
            commands.append({"tool": "run_command", "cmd": match.group(1).strip()})
        for match in patterns["create_folder"].finditer(ai_response):
            commands.append({"tool": "create_folder", "path": match.group(1).strip()})
        for match in patterns["delete_file"].finditer(ai_response):
            commands.append({"tool": "delete_file", "path": match.group(1).strip()})
        for match in patterns["read_file"].finditer(ai_response):
            commands.append({"tool": "read_file", "path": match.group(1).strip()})
        for match in patterns["list_dir"].finditer(ai_response):
            commands.append({"tool": "list_dir", "path": match.group(1).strip()})
        for match in patterns["search_codebase"].finditer(ai_response):
            commands.append({"tool": "search_codebase", "pattern": match.group(1), "path": match.group(2).strip()})
        for match in patterns["ask_user"].finditer(ai_response):
            commands.append({"tool": "ask_user", "question": match.group(1).strip()})
            
        return commands"""

# Replace the old parse_tools method
content = re.sub(r'    def parse_tools\(self, ai_response\):.*?(?=\Z|\n\S)', new_parser, content, flags=re.DOTALL)

with open("caleb_studio_builder/builder/code_generator.py", "w") as f:
    f.write(content)

print("[+] Code Generator updated with full 10-tool regex schema.")
