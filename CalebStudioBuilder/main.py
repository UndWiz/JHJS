import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSplitter, QTextEdit, QComboBox, 
                             QPushButton, QLabel, QCheckBox, QTabWidget)
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
        self.setWindowTitle("CALEB: Creative Automation & Local Engineering Builder (v1.1)")
        self.setGeometry(100, 100, 1600, 900)
        
        # Patched Stylesheet to fix Checkboxes and style Tabs
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
            QTextEdit { background-color: #1e1e1e; color: #d4d4d4; border: 1px solid #333; border-radius: 4px; }
            QTreeView { background-color: #181818; }
            QPushButton { background-color: #333; color: white; border: 1px solid #444; padding: 6px; border-radius: 4px; }
            QPushButton:hover { background-color: #444; }
            QCheckBox { color: #e0e0e0; spacing: 5px; font-weight: bold; }
            QCheckBox::indicator { width: 16px; height: 16px; background-color: #222; border: 1px solid #555; border-radius: 3px; }
            QCheckBox::indicator:checked { background-color: #00ff00; border: 1px solid #00ff00; }
            QTabBar::tab { background: #252525; padding: 10px 20px; color: #aaa; border: 1px solid #121212; }
            QTabBar::tab:selected { background: #1e1e1e; color: #00ff00; border-bottom: 2px solid #00ff00; font-weight: bold; }
            QTabWidget::pane { border: 1px solid #333; }
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
        
        # Left Panel (Filesystem & Quick History)
        left_panel = QSplitter(Qt.Vertical)
        self.fs_panel = FilesystemPanel()
        self.fs_panel.tree.clicked.connect(self.load_file_to_editor)
        left_panel.addWidget(self.fs_panel)
        
        history_container = QWidget()
        history_layout = QVBoxLayout(history_container)
        self.history_chat = QTextEdit()
        self.history_chat.setReadOnly(True)
        history_layout.addWidget(QLabel("<b>Log History</b>"))
        history_layout.addWidget(self.history_chat)
        left_panel.addWidget(history_container)
        
        # Center Panel (Main Work Area)
        center_panel = QSplitter(Qt.Vertical)
        
        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        self.chk_preview = QCheckBox("Preview Changes")
        self.chk_preview.toggled.connect(self.update_modes)
        self.chk_sandbox = QCheckBox("Execution Sandbox")
        self.chk_sandbox.toggled.connect(self.update_modes)
        top_layout.addWidget(self.chk_preview)
        top_layout.addWidget(self.chk_sandbox)
        top_layout.addStretch()
        
        self.sys_label = QLabel("<b>SYS:</b> CPU: --% | RAM: --/--GB | VRAM: --/--GB")
        top_layout.addWidget(self.sys_label)
        
        self.kill_switch = QPushButton("EMERGENCY STOP")
        self.kill_switch.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold;")
        self.kill_switch.clicked.connect(self.emergency_stop)
        top_layout.addWidget(self.kill_switch)
        center_panel.addWidget(top_bar)
        
        # THE NEW CENTRAL TAB SYSTEM
        self.center_tabs = QTabWidget()
        
        # Tab 1: AI Chat & Output View
        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        self.chat_view.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-size: 14px; padding: 10px;")
        self.center_tabs.addTab(self.chat_view, "AI Chat")
        
        # Tab 2: Code Editor View
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_tools = QHBoxLayout()
        self.lbl_current_file = QLabel("<b>Workspace:</b> No file selected")
        self.btn_save_file = QPushButton("Save File")
        self.btn_save_file.clicked.connect(self.save_current_file)
        editor_tools.addWidget(self.lbl_current_file)
        editor_tools.addStretch()
        editor_tools.addWidget(self.btn_save_file)
        
        self.code_editor = QTextEdit()
        self.code_editor.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: monospace; font-size: 13px;")
        editor_layout.addLayout(editor_tools)
        editor_layout.addWidget(self.code_editor)
        self.center_tabs.addTab(editor_container, "Code Editor")
        
        center_panel.addWidget(self.center_tabs)
        
        # Input Box
        self.input_box = ChatInputBox(self.handle_input)
        center_panel.addWidget(self.input_box)
        
        # Right Panel (Settings & Logs)
        right_panel = QSplitter(Qt.Vertical)
        self.settings_panel = SettingsPanel(hardware_monitor=self.hw_monitor)
        right_panel.addWidget(self.settings_panel)
        self.logs_panel = LogsPanel()
        right_panel.addWidget(self.logs_panel)
        
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(center_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([300, 900, 400])
        self.setCentralWidget(main_splitter)

    def load_file_to_editor(self, index):
        file_path = self.fs_panel.model.filePath(index)
        if os.path.isfile(file_path):
            self.current_open_file = file_path
            self.lbl_current_file.setText(f"<b>Workspace:</b> {os.path.basename(file_path)}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.code_editor.setPlainText(f.read())
                # Auto-switch to the Code Editor tab when a file is clicked
                self.center_tabs.setCurrentIndex(1)
            except Exception as e:
                self.code_editor.setPlainText(f"Error loading file: {str(e)}")

    def save_current_file(self):
        if self.current_open_file:
            content = self.code_editor.toPlainText()
            try:
                with open(self.current_open_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.logs_panel.append_log(f"[SYS] File saved manually: {self.current_open_file}")
                self.controller.indexer.scan_project()
            except Exception as e:
                self.logs_panel.append_log(f"[!] Error saving file: {str(e)}")

    def update_modes(self):
        self.controller.set_modes(self.chk_preview.isChecked(), self.chk_sandbox.isChecked())

    def init_timers(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_hardware_stats)
        self.timer.start(2000)

    def update_hardware_stats(self):
        stats = self.hw_monitor.get_stats()
        self.sys_label.setText(f"<b>SYS:</b> CPU: {stats['cpu']}% | RAM: {stats['ram_used']}/{stats['ram_total']}GB | VRAM: {stats['vram_used']}/{stats['vram_total']}GB")

    def handle_input(self, text):
        self.controller.update_config(self.settings_panel.get_config())
        self.history_chat.append(f"<b>You:</b> {text}")
        
        # Display user input in the main Chat Tab
        self.chat_view.append(f"<span style='color:#00ff00;'><b>You:</b></span> {text}<br>")
        
        self.input_box.set_processing_state(True)
        self.active_thread = AITaskThread(self.controller, text)
        self.active_thread.log_signal.connect(self.logs_panel.append_log)
        self.active_thread.result_signal.connect(self.on_task_complete)
        self.active_thread.start()

    def emergency_stop(self):
        if self.active_thread and self.active_thread.isRunning():
            self.active_thread.kill()
            self.active_thread = None
            self.logs_panel.append_log("[!] EMERGENCY STOP TRIGGERED. Task Aborted.")
            self.input_box.set_processing_state(False)

    def on_task_complete(self, raw_ai, execution_results):
        self.history_chat.append(f"<b>CALEB:</b> Task complete.")
        
        # Format the AI's raw XML/Text output for HTML display
        safe_ai_text = raw_ai.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
        self.chat_view.append(f"<span style='color:#00ffff;'><b>CALEB:</b></span><br>{safe_ai_text}<br>")
        
        for res in execution_results:
            self.logs_panel.append_log(f"[RESULT] {res}")
            # If the command outputted text (like running a python script), print it to the chat view!
            if "[CMD SUCCESS]" in res or "[CMD FAILED]" in res:
                safe_res = res.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
                self.chat_view.append(f"<span style='color:#aaaaaa;'><i>Terminal Output: {safe_res}</i></span><br>")
                
        self.chat_view.append("<hr>")
        
        # Auto-switch back to the Chat view so you can read the response
        self.center_tabs.setCurrentIndex(0)

        if self.current_open_file and any(self.current_open_file in r for r in execution_results):
             with open(self.current_open_file, 'r', encoding='utf-8') as f:
                self.code_editor.setPlainText(f.read())
                
        self.input_box.set_processing_state(False)
        self.active_thread = None

    def load_workspace_state(self):
        pass

    def closeEvent(self, event):
        if self.active_thread and self.active_thread.isRunning():
            self.active_thread.kill()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CalebStudio()
    window.show()
    sys.exit(app.exec_())
