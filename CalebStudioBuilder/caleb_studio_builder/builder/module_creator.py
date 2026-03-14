import os
from caleb_studio_builder.core.file_manager import FileManager

class ModuleCreator:
    """Scaffolds new python modules using the standardized CALEB templates."""
    def __init__(self, project_root):
        self.fm = FileManager(project_root)
        self.template_path = os.path.join(project_root, "caleb_studio_builder", "templates", "python_module_template.py")

    def create_module(self, target_path):
        if not os.path.exists(self.template_path):
            return False, "Template not found."
            
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        try:
            self.fm.write_file(target_path, template_content)
            return True, f"Module scaffolded at {target_path}"
        except Exception as e:
            return False, str(e)

if __name__ == "__main__":
    print("[+] Module Creator Module initialized.")
