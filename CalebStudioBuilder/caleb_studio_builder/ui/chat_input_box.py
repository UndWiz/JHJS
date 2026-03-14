from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton

class ChatInputBox(QWidget):
    def __init__(self, execute_callback):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(80)
        self.input_field.setPlaceholderText("Awaiting CALEB directives...")
        
        self.submit_btn = QPushButton("Execute CALEB Tool Sequence")
        self.submit_btn.clicked.connect(self._handle_submit)
        
        self.execute_callback = execute_callback
        
        layout.addWidget(self.input_field)
        layout.addWidget(self.submit_btn)
        
    def _handle_submit(self):
        text = self.input_field.toPlainText().strip()
        if text:
            self.execute_callback(text)
            self.input_field.clear()
            
    def set_processing_state(self, is_processing):
        self.submit_btn.setEnabled(not is_processing)
        self.submit_btn.setText("Processing..." if is_processing else "Execute CALEB Tool Sequence")
