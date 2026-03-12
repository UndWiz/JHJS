from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QComboBox, QHBoxLayout
from PyQt5.QtGui import QColor, QTextCharFormat, QTextCursor

class LogsPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Top controls for filtering
        ctrl_layout = QHBoxLayout()
        ctrl_layout.addWidget(QLabel("<b>Execution Logs</b>"))
        ctrl_layout.addStretch()
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Success", "Warning", "Error", "Info"])
        self.filter_combo.currentTextChanged.connect(self._apply_filter)
        ctrl_layout.addWidget(QLabel("Filter:"))
        ctrl_layout.addWidget(self.filter_combo)
        
        layout.addLayout(ctrl_layout)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("background-color: #0c0c0c; color: #d4d4d4; font-family: monospace;")
        
        layout.addWidget(self.text_edit)
        
        # Store raw logs for filtering
        self._raw_logs = []
        
    def append_log(self, msg):
        self._raw_logs.append(msg)
        self._render_log(msg)
        
    def _render_log(self, msg):
        current_filter = self.filter_combo.currentText()
        is_error = "[!]" in msg or "Error" in msg or "failed" in msg.lower()
        is_warning = "Warning" in msg
        is_success = "[RESULT]" in msg or "success" in msg.lower()
        
        if current_filter == "Error" and not is_error: return
        if current_filter == "Warning" and not is_warning: return
        if current_filter == "Success" and not is_success: return
        if current_filter == "Info" and (is_error or is_warning or is_success): return

        # Apply CALEB blueprint color coding
        color = "#d4d4d4" # Default gray
        if is_error:
            color = "#ff4c4c" # Red
        elif is_warning:
            color = "#ffcc00" # Yellow
        elif is_success:
            color = "#00ff00" # Green
            
        formatted_msg = f'<span style="color: {color};">{msg}</span>'
        self.text_edit.append(formatted_msg)
        
        scrollbar = self.text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _apply_filter(self):
        self.text_edit.clear()
        for log in self._raw_logs:
            self._render_log(log)
