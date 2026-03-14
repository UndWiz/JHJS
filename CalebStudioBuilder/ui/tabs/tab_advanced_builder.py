import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
                             QTextEdit, QLabel, QCheckBox, QTabWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

# Import local agent stuff
try:
    from caleb_studio_builder.core.agent_controller import AgentController
    from caleb_studio_builder.ui.filesystem_panel import FilesystemPanel
    from caleb_studio_builder.ui.logs_panel import LogsPanel
    from caleb_studio_builder.ui.chat_input_box import ChatInputBox
    from caleb_studio_builder.ui.settings_panel import SettingsPanel
    from caleb_studio_builder.utils.hardware_monitor import HardwareMonitor
except ImportError:
    pass

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
        if self.controller:
            raw, results = self.controller.process_user_input(
                self.prompt, log_callback=lambda msg: self.log_signal.emit(msg) if not self.is_killed else None
            )
            if not self.is_killed: self.result_signal.emit(raw, results)
    def kill(self):
        self.is_killed = True
        self.terminate()

class AdvancedBuilderWidget(QWidget):
    def __init__(self, parent_main):
        super().__init__()
        self.parent_main = parent_main
        try:
            self.controller = AgentController(os.getcwd())
            self.hw_monitor = HardwareMonitor()
        except:
            self.controller = None
            self.hw_monitor = None
            
        self.active_thread = None
        self.current_open_file = None
        
        self.setStyleSheet("""
            QWidget { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
            QTextEdit { background-color: #1e1e1e; color: #d4d4d4; border: 1px solid #333; border-radius: 4px; }
            QTreeView { background-color: #181818; }
            QPushButton { background-color: #333; color: white; border: 1px solid #444; padding: 6px; border-radius: 4px; }
            QCheckBox { color: #e0e0e0; spacing: 5px; font-weight: bold; }
            QTabBar::tab { background: #252525; padding: 10px 20px; color: #aaa; border: 1px solid #121212; }
            QTabBar::tab:selected { background: #1e1e1e; color: #00ff00; border-bottom: 2px solid #00ff00; font-weight: bold; }
        """)

        main_splitter = QSplitter(Qt.Horizontal)
        
        left_panel = QSplitter(Qt.Vertical)
        try:
            self.fs_panel = FilesystemPanel()
            self.fs_panel.tree.clicked.connect(self.load_file_to_editor)
            left_panel.addWidget(self.fs_panel)
        except:
            pass
        
        history_container = QWidget()
        history_layout = QVBoxLayout(history_container)
        self.history_chat = QTextEdit()
        self.history_chat.setReadOnly(True)
        history_layout.addWidget(QLabel("<b>Log History</b>"))
        history_layout.addWidget(self.history_chat)
        left_panel.addWidget(history_container)
        
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
        try:
            self.input_box = ChatInputBox(self.handle_input)
            center_panel.addWidget(self.input_box)
        except:
            pass
        
        right_panel = QSplitter(Qt.Vertical)
        try:
            self.settings_panel = SettingsPanel(hardware_monitor=self.hw_monitor)
            self.logs_panel = LogsPanel()
            right_panel.addWidget(self.settings_panel)
            right_panel.addWidget(self.logs_panel)
        except:
            pass
        
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(center_panel)
        main_splitter.addWidget(right_panel)
        
        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(main_splitter)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_hardware_stats)
        self.timer.start(2000)

    def update_hardware_stats(self):
        if hasattr(self, 'hw_monitor') and self.hw_monitor:
            stats = self.hw_monitor.get_stats()
            self.sys_label.setText(f"<b>SYS:</b> CPU: {stats['cpu']}% | RAM: {stats['ram_used']}/{stats['ram_total']}GB | VRAM: {stats['vram_used']}/{stats['vram_total']}GB")

    def load_file_to_editor(self, index):
        if hasattr(self, 'fs_panel'):
            file_path = self.fs_panel.model.filePath(index)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as f: self.code_editor.setPlainText(f.read())
                self.center_tabs.setCurrentIndex(1)

    def handle_input(self, text):
        self.chat_view.append(f"<span style='color:#00ff00;'><b>You:</b></span> {text}<br>")
        if hasattr(self, 'controller') and self.controller:
            self.active_thread = AITaskThread(self.controller, text)
            if hasattr(self, 'logs_panel'):
                self.active_thread.log_signal.connect(self.logs_panel.append_log)
            self.active_thread.result_signal.connect(self.on_task_complete) 
            self.active_thread.start()

    def on_task_complete(self, raw_ai, execution_results):
        safe_ai_text = raw_ai.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
        self.chat_view.append(f"<span style='color:#00ffff;'><b>CALEB:</b></span><br>{safe_ai_text}<br>")
        for res in execution_results:
            if hasattr(self, 'logs_panel'):
                self.logs_panel.append_log(f"[RESULT] {res}")
            if "[CMD SUCCESS]" in res or "[CMD FAILED]" in res:
                safe_res = res.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
                self.chat_view.append(f"<span style='color:#aaaaaa;'><i>Terminal Output: {safe_res}</i></span><br>")
        self.chat_view.append("<hr>")
        if self.current_open_file and any(self.current_open_file in r for r in execution_results):
             with open(self.current_open_file, 'r', encoding='utf-8') as f: self.code_editor.setPlainText(f.read())
        if hasattr(self, 'input_box') and hasattr(self.input_box, 'set_processing_state'): 
            self.input_box.set_processing_state(False)
        self.active_thread = None
