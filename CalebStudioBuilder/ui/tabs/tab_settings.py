from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget
import os

class SettingsProjectWidget(QWidget):
    def __init__(self, parent_main):
        super().__init__()
        self.parent_main = parent_main
        self.layout = QVBoxLayout(self)
        
        # Project Scaffolding
        self.layout.addWidget(QLabel("<b>STUDIO PROJECT MANAGER</b>"))
        self.name_in = QLineEdit()
        self.name_in.setPlaceholderText("Enter New Project Name (e.g., Episode_1)")
        self.name_in.setStyleSheet("background-color: #1e1e1e; padding: 10px; color: white;")
        self.layout.addWidget(self.name_in)
        
        self.create_btn = QPushButton("SCAFFOLD PROJECT STRUCTURE")
        self.create_btn.setStyleSheet("background-color: #00ff00; color: black; font-weight: bold; padding: 12px;")
        self.create_btn.clicked.connect(self.create_project)
        self.layout.addWidget(self.create_btn)
        
        # System Paths Status
        self.layout.addWidget(QLabel("<hr><b>System Paths & Engine Status</b>"))
        self.status_list = QListWidget()
        self.status_list.setStyleSheet("background-color: #121214; color: #aaaaaa; border: 1px solid #333;")
        self.check_engines()
        self.layout.addWidget(self.status_list)
        
        self.layout.addStretch()

    def create_project(self):
        name = self.name_in.text().strip()
        if name and hasattr(self.parent_main, 'vault'):
            path = self.parent_main.vault.create_project(name)
            if hasattr(self.parent_main, 'simple_chat'):
                self.parent_main.simple_chat.append(f"<span style='color:cyan;'>[SYS] Scaffolding deployed for '{name}' at {path}</span>")
            self.name_in.clear()

    def check_engines(self):
        base = os.path.expanduser("~/CalebStudioBuilder/models")
        checks = {
            "SDXL Base (Images)": os.path.exists(os.path.join(base, "diffusion/sd_xl_base_1.0.safetensors")),
            "AnimateDiff (Video)": os.path.exists(os.path.join(base, "video/mm_sd_v15_v2.ckpt")),
            "Real-ESRGAN (Upscale)": os.path.exists(os.path.join(base, "video/RealESRGAN_x4.pth"))
        }
        for engine, exists in checks.items():
            status = "🟢 ONLINE" if exists else "🔴 OFFLINE / MISSING"
            self.status_list.addItem(f"{engine}: {status}")
