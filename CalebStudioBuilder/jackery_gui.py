import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSplitter, QTextEdit, QComboBox, 
                             QPushButton, QLabel, QCheckBox, QTabWidget, QFrame, QListWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

# Import your local modules
try:
    from caleb_studio_builder.core.agent_controller import AgentController
    from caleb_studio_builder.ui.filesystem_panel import FilesystemPanel
    from caleb_studio_builder.ui.logs_panel import LogsPanel
    from caleb_studio_builder.ui.chat_input_box import ChatInputBox
    from caleb_studio_builder.ui.settings_panel import SettingsPanel
    from caleb_studio_builder.utils.hardware_monitor import HardwareMonitor
except ImportError as e:
    print(f"Warning: Local modules not found, check pathing. Error: {e}")

# --- YOUR ORIGINAL AI THREAD LOGIC ---
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

# --- THE ADVANCED BUILDER WIDGET ---
class AdvancedBuilderWidget(QWidget):
    def __init__(self, parent_main):
        super().__init__()
        self.parent_main = parent_main
        self.controller = AgentController(os.getcwd())
        self.hw_monitor = HardwareMonitor()
        self.active_thread = None
        self.current_open_file = None
        
        # Fixed Stylesheet (Checkbox indicators restored)
        self.setStyleSheet("""
            QWidget { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
            QTextEdit { background-color: #1e1e1e; color: #d4d4d4; border: 1px solid #333; border-radius: 4px; }
            QTreeView { background-color: #181818; }
            QPushButton { background-color: #333; color: white; border: 1px solid #444; padding: 6px; border-radius: 4px; }
            QCheckBox { color: #e0e0e0; spacing: 5px; font-weight: bold; }
            QCheckBox::indicator { width: 16px; height: 16px; background-color: #222; border: 1px solid #555; border-radius: 3px; }
            QCheckBox::indicator:checked { background-color: #00ff00; border: 1px solid #00ff00; }
            QTabBar::tab { background: #252525; padding: 10px 20px; color: #aaa; border: 1px solid #121212; }
            QTabBar::tab:selected { background: #1e1e1e; color: #00ff00; border-bottom: 2px solid #00ff00; font-weight: bold; }
        """)

        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel
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
        
        # Center Panel
        center_panel = QSplitter(Qt.Vertical)
        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        self.chk_preview = QCheckBox("Preview Changes")
        self.chk_sandbox = QCheckBox("Execution Sandbox")
        top_layout.addWidget(self.chk_preview)
        top_layout.addWidget(self.chk_sandbox)
        top_layout.addStretch()
        
        self.sys_label = QLabel("<b>SYS:</b> CPU: --% | RAM: --/--GB | VRAM: --/--GB")
        top_layout.addWidget(self.sys_label)
        
        self.kill_switch = QPushButton("EMERGENCY STOP")
        self.kill_switch.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold;")
        self.kill_switch.clicked.connect(self.emergency_stop) # Wired up
        top_layout.addWidget(self.kill_switch)
        center_panel.addWidget(top_bar)
        
        self.center_tabs = QTabWidget()
        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        self.center_tabs.addTab(self.chat_view, "AI Chat")
        
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        self.code_editor = QTextEdit()
        editor_layout.addWidget(self.code_editor)
        self.center_tabs.addTab(editor_container, "Code Editor")
        
        center_panel.addWidget(self.center_tabs)
        self.input_box = ChatInputBox(self.handle_input)
        center_panel.addWidget(self.input_box)
        
        # Right Panel
        right_panel = QSplitter(Qt.Vertical)
        self.settings_panel = SettingsPanel(hardware_monitor=self.hw_monitor)
        self.logs_panel = LogsPanel()
        right_panel.addWidget(self.settings_panel)
        right_panel.addWidget(self.logs_panel)
        
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(center_panel)
        main_splitter.addWidget(right_panel)
        
        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(main_splitter)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_hardware_stats)
        self.timer.start(2000)

    def update_hardware_stats(self):
        stats = self.hw_monitor.get_stats()
        self.sys_label.setText(f"<b>SYS:</b> CPU: {stats['cpu']}% | RAM: {stats['ram_used']}/{stats['ram_total']}GB | VRAM: {stats['vram_used']}/{stats['vram_total']}GB")

    def load_file_to_editor(self, index):
        file_path = self.fs_panel.model.filePath(index)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f: self.code_editor.setPlainText(f.read())
            self.center_tabs.setCurrentIndex(1)

    def handle_input(self, text):
        self.chat_view.append(f"<span style='color:#00ff00;'><b>You:</b></span> {text}<br>")
        self.active_thread = AITaskThread(self.controller, text)
        self.active_thread.log_signal.connect(self.logs_panel.append_log)
        self.active_thread.result_signal.connect(self.on_task_complete) # Wired up
        self.active_thread.start()

    # Restored Methods for Task Completion and Kill Switch
    def emergency_stop(self):
        if self.active_thread and self.active_thread.isRunning():
            self.active_thread.kill()
            self.active_thread = None
            self.logs_panel.append_log("[!] EMERGENCY STOP TRIGGERED. Task Aborted.")
            if hasattr(self.input_box, 'set_processing_state'):
                self.input_box.set_processing_state(False)

    def on_task_complete(self, raw_ai, execution_results):
        self.history_chat.append(f"<b>CALEB:</b> Task complete.")
        safe_ai_text = raw_ai.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
        self.chat_view.append(f"<span style='color:#00ffff;'><b>CALEB:</b></span><br>{safe_ai_text}<br>")
        
        for res in execution_results:
            self.logs_panel.append_log(f"[RESULT] {res}")
            if "[CMD SUCCESS]" in res or "[CMD FAILED]" in res:
                safe_res = res.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
                self.chat_view.append(f"<span style='color:#aaaaaa;'><i>Terminal Output: {safe_res}</i></span><br>")
                
        self.chat_view.append("<hr>")
        self.center_tabs.setCurrentIndex(0)

        if self.current_open_file and any(self.current_open_file in r for r in execution_results):
             with open(self.current_open_file, 'r', encoding='utf-8') as f:
                self.code_editor.setPlainText(f.read())
                
        if hasattr(self.input_box, 'set_processing_state'):
            self.input_box.set_processing_state(False)
        self.active_thread = None


# --- THE MASTER STUDIO SHELL ---
class JackeryGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jack Hole Jackery Studios")
        self.setGeometry(100, 100, 1600, 950)
        self.setStyleSheet("background-color: #121214; color: #e6e6eb;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Header
        header_area = QHBoxLayout()
        studio_lbl = QLabel("Jack Hole Jackery Studios")
        studio_lbl.setStyleSheet("font-size: 14pt; font-weight: bold; color: #00ff00;")
        self.adv_toggle = QCheckBox("ADVANCED BUILDER")
        self.adv_toggle.setStyleSheet("color: #e6a822;")
        self.adv_toggle.toggled.connect(self.toggle_builder)
        
        header_area.addWidget(studio_lbl)
        header_area.addStretch()
        header_area.addWidget(self.adv_toggle)
        self.main_layout.addLayout(header_area)

        # Tabs
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # --- CALEB Hub Tab ---
        self.caleb_hub_tab = QWidget()
        self.hub_layout = QVBoxLayout(self.caleb_hub_tab)
        
        # Simple View (ChatGPT/Gemini Clone)
        self.simple_view = QWidget()
        sv_layout = QHBoxLayout(self.simple_view)
        sv_layout.setContentsMargins(0,0,0,0)
        
        # Sidebar for Chat History
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("background-color: #1a1a1e; border-right: 1px solid #333;")
        sidebar_layout = QVBoxLayout(sidebar)
        new_chat_btn = QPushButton("+ New Chat")
        new_chat_btn.setStyleSheet("background-color: #2a2a30; padding: 12px; border-radius: 6px; font-weight: bold; color: #e6e6eb;")
        history_list = QTextEdit()
        history_list.setReadOnly(True)
        history_list.setStyleSheet("border: none; background-color: transparent;")
        history_list.append("<b>Recent Chats</b><br><br>• Project Setup<br>• Script Gen")
        sidebar_layout.addWidget(new_chat_btn)
        sidebar_layout.addWidget(history_list)
        
        # Main Chat Area
        main_chat_area = QWidget()
        main_chat_layout = QVBoxLayout(main_chat_area)
        self.simple_chat = QTextEdit()
        self.simple_chat.setReadOnly(True)
        self.simple_chat.setStyleSheet("background-color: #121214; border: none; padding: 20px; font-size: 14px;")
        self.simple_chat.append("<b>[SYSTEM]</b> Sup JackHole.")
        
        # Bottom Input Area
        input_container = QHBoxLayout()
        from PyQt5.QtWidgets import QLineEdit
        self.simple_input = QLineEdit()
        self.simple_input.setPlaceholderText("Message CALEB...")
        self.simple_input.setStyleSheet("background-color: #2a2a30; padding: 15px; border-radius: 10px; border: 1px solid #444; font-size: 14px;")
        simple_send = QPushButton("Send")
        simple_send.setStyleSheet("background-color: #5078c8; padding: 15px 25px; border-radius: 10px; font-weight: bold;")
        input_container.addWidget(self.simple_input)
        input_container.addWidget(simple_send)
        
        main_chat_layout.addWidget(self.simple_chat)
        main_chat_layout.addLayout(input_container)
        
        sv_layout.addWidget(sidebar)
        sv_layout.addWidget(main_chat_area)

        # Advanced View (Your CalebStudio)
        self.advanced_builder = AdvancedBuilderWidget(self)
        
        self.hub_layout.addWidget(self.simple_view)
        self.hub_layout.addWidget(self.advanced_builder)
        self.advanced_builder.hide()

        self.tabs.addTab(self.caleb_hub_tab, "CALEB Hub")
        
        # Placeholders
        for t in ["Image Forge", "Video Motion VFX", "Audio Lab", "Settings"]:
            self.tabs.addTab(QLabel(f"{t} Module Offline"), t)

    def toggle_builder(self, checked):
        if checked:
            self.simple_view.hide()
            self.advanced_builder.show()
        else:
            self.advanced_builder.hide()
            self.simple_view.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JackeryGUI()
    window.show()
    sys.exit(app.exec_())
