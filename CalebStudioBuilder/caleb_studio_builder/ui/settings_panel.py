from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QFormLayout, 
                             QCheckBox, QSlider, QSpinBox, QLineEdit, QListWidget, 
                             QAbstractItemView, QTabWidget, QScrollArea)
from PyQt5.QtCore import Qt

class SettingsPanel(QWidget):
    def __init__(self, hardware_monitor=None):
        super().__init__()
        self.hw_monitor = hardware_monitor
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        
        # --- Tab 1: AI Model Management ---
        ai_tab = QWidget()
        ai_layout = QVBoxLayout(ai_tab)
        
        ai_group = QGroupBox("Inference Routing")
        ai_form = QFormLayout()
        
        self.chk_hybrid = QCheckBox("Enable Hybrid Model Mode")
        ai_form.addRow(self.chk_hybrid)
        
        self.list_engines = QListWidget()
        self.list_engines.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_engines.addItems(["qwen2.5-coder:7b (Local)", "qwen2.5:14b (Local)", "llama3:8b (Local)"])
        # Select default
        self.list_engines.item(0).setSelected(True)
        self.list_engines.setMaximumHeight(80)
        
        ai_form.addRow("Active Local Engines:", self.list_engines)
        ai_group.setLayout(ai_form)
        ai_layout.addWidget(ai_group)
        ai_layout.addStretch()
        
        self.tabs.addTab(ai_tab, "AI Config")
        
        # --- Tab 2: Hardware Limits ---
        hw_tab = QWidget()
        hw_layout = QVBoxLayout(hw_tab)
        
        hw_group = QGroupBox("System Resource Caps")
        hw_form = QFormLayout()
        
        self.slider_vram = QSlider(Qt.Horizontal)
        self.slider_vram.setMinimum(1)
        self.slider_vram.setMaximum(16)
        self.slider_vram.setValue(15)
        self.slider_vram.setTickPosition(QSlider.TicksBelow)
        self.slider_vram.setTickInterval(1)
        
        self.spin_cpu = QSpinBox()
        self.spin_cpu.setMinimum(1)
        self.spin_cpu.setMaximum(12)
        self.spin_cpu.setValue(6)
        
        self.spin_ram = QSpinBox()
        self.spin_ram.setMinimum(1)
        self.spin_ram.setMaximum(16)
        self.spin_ram.setValue(14)
        
        hw_form.addRow("GPU VRAM Cap (GB):", self.slider_vram)
        hw_form.addRow("CPU Thread Limit:", self.spin_cpu)
        hw_form.addRow("RAM Usage Limit (GB):", self.spin_ram)
        
        hw_group.setLayout(hw_form)
        hw_layout.addWidget(hw_group)
        hw_layout.addStretch()
        
        self.tabs.addTab(hw_tab, "Hardware")
        
        # --- Tab 3: Environment ---
        env_tab = QWidget()
        env_layout = QVBoxLayout(env_tab)
        
        env_group = QGroupBox("Python Context")
        env_form = QFormLayout()
        
        self.txt_workdir = QLineEdit("${HOME}/CalebStudioBuilder")
        self.chk_venv = QCheckBox("Force venv activation on script start")
        self.chk_venv.setChecked(True)
        
        env_form.addRow("Working Directory:", self.txt_workdir)
        env_form.addRow(self.chk_venv)
        
        env_group.setLayout(env_form)
        env_layout.addWidget(env_group)
        env_layout.addStretch()
        
        self.tabs.addTab(env_tab, "Environment")
        
        main_layout.addWidget(self.tabs)
        
    def get_config(self):
        """Returns the current state of the settings UI for the Controller."""
        return {
            "ai": {
                "hybrid_mode": self.chk_hybrid.isChecked(),
                "active_engines": [item.text() for item in self.list_engines.selectedItems()]
            },
            "hardware": {
                "vram_cap": self.slider_vram.value(),
                "cpu_threads": self.spin_cpu.value(),
                "ram_limit": self.spin_ram.value()
            },
            "environment": {
                "working_dir": self.txt_workdir.text(),
                "require_venv": self.chk_venv.isChecked()
            }
        }
