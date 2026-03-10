import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSplitter, QTextEdit, QComboBox, 
                             QPushButton, QLabel, QCheckBox, QTabWidget, QFileSystemModel)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

from caleb_studio_builder.core.agent_controller import AgentController
from caleb_studio_builder.ui.filesystem_panel import FilesystemPanel
from caleb_studio_builder.ui.logs_panel import LogsPanel
from caleb_studio_builder.ui.chat_input_box import ChatInputBox
from caleb_studio_builder.ui.settings_panel import SettingsPanel
from caleb_studio_builder.utils.hardware_monitor import HardwareMonitor

class AITaskThread(QThread):
    log_signal = pyqtSignal(str)
    result_signal = pyqtSignal(str, list)

    def __init__(self, controller, prompt):
        super().__init__()
        self.controller = controller
        self.prompt = prompt
        self.is_killed = False

    def run(self):
        if self.is_killed: return
        raw, results = self.controller.process_user_input(
            self.prompt, 
            log_callback=lambda msg: self.log_signal.emit(msg) if not self.is_killed else None
        )
        if not self.is_killed:
            self.result_signal.emit(raw, results)

    def kill(self):
        self.is_killed = True
        self.terminate()

class CalebStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CALEB: Creative Automation & Local Engineering Builder (v1.0.0-FINAL)")
        self.setGeometry(100, 100, 1600, 900)
        
        # Apply Dark Theme
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
            QTextEdit { background-color: #1e1e1e; color: #d4d4d4; border: 1px solid #333; border-radius: 4px; }
            QTreeView { background-color: #181818; }
            QPushButton { background-color: #333; color: white; border: 1px solid #444; padding: 6px; border-radius: 4px; }
            QPushButton:hover { background-color: #444; }
            QTabBar::tab { background: #252525; padding: 8px; }
            QTabBar::tab:selected { background: #333; border-bottom: 2px solid #00ff00; }
        """)

        self.controller = AgentController(os.getcwd())
        self.hw_monitor = HardwareMonitor()
        self.active_thread = None
        self.current_open_file = None
        
        self.init_ui()
        self.init_timers()
        self.load_workspace_state()

    def init_ui(self):
        main_splitter = QSplitter(Qt.Horizontal)
        
        left_panel = QSplitter(Qt.Vertical)
        self.fs_panel = FilesystemPanel()
        self.fs_panel.tree.clicked.connect(self.load_file_to_editor)
        left_panel.addWidget(self.fs_panel)
        
        history_container = QWidget(); history_layout = QVBoxLayout(history_container)
        self.history_chat = QTextEdit(); self.history_chat.setReadOnly(True)
        history_layout.addWidget(QLabel("<b>Chat History</b>")); history_layout.addWidget(self.history_chat)
        left_panel.addWidget(history_container)
        
        center_panel = QSplitter(Qt.Vertical)
        top_bar = QWidget(); top_layout = QHBoxLayout(top_bar)
        self.chk_preview = QCheckBox("Preview"); self.chk_sandbox = QCheckBox("Sandbox")
        top_layout.addWidget(self.chk_preview); top_layout.addWidget(self.chk_sandbox); top_layout.addStretch()
        self.sys_label = QLabel("SYS: CPU: --% | RAM: --GB | VRAM: --GB")
        top_layout.addWidget(self.sys_label)
        center_panel.addWidget(top_bar)
        
        self.code_editor = QTextEdit()
        center_panel.addWidget(self.code_editor)
        self.input_box = ChatInputBox(self.handle_input)
        center_panel.addWidget(self.input_box)
        
        right_panel = QSplitter(Qt.Vertical)
        self.settings_panel = SettingsPanel(hardware_monitor=self.hw_monitor)
        right_panel.addWidget(self.settings_panel)
        self.logs_panel = LogsPanel()
        right_panel.addWidget(self.logs_panel)
        
        main_splitter.addWidget(left_panel); main_splitter.addWidget(center_panel); main_splitter.addWidget(right_panel)
        self.setCentralWidget(main_splitter)

    def load_file_to_editor(self, index):
        file_path = self.fs_panel.model.filePath(index)
        if os.path.isfile(file_path):
            self.current_open_file = file_path
            with open(file_path, 'r', encoding='utf-8') as f:
                self.code_editor.setPlainText(f.read())

    def handle_input(self, text):
        self.history_chat.append(f"<b>You:</b> {text}")
        self.input_box.set_processing_state(True)
        self.active_thread = AITaskThread(self.controller, text)
        self.active_thread.log_signal.connect(self.logs_panel.append_log)
        self.active_thread.result_signal.connect(self.on_task_complete)
        self.active_thread.start()

    def on_task_complete(self, raw, res):
        self.history_chat.append("<b>CALEB:</b> Task complete.")
        self.input_box.set_processing_state(False)

    def init_timers(self):
        self.timer = QTimer(); self.timer.timeout.connect(self.update_stats); self.timer.start(2000)

    def update_stats(self):
        s = self.hw_monitor.get_stats()
        self.sys_label.setText(f"SYS: CPU: {s['cpu']}% | RAM: {s['ram_used']}GB | VRAM: {s['vram_used']}GB")

    def load_workspace_state(self):
        pass # Placeholder for state logic

    def closeEvent(self, event):
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CalebStudio()
    window.show()
    sys.exit(app.exec_())
