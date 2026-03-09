# gui/caleb_gui.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit,
    QLineEdit, QPushButton
)

from core.caleb_task_manager import CalebTaskManager

class CalebGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Caleb Studio Builder")
        self.setGeometry(100, 100, 800, 600)

        # Task manager backend
        self.task_manager = CalebTaskManager()

        # UI
        self.layout = QVBoxLayout()
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)

        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Enter a command (type 'help')")
        self.submit_button = QPushButton("Send")
        self.submit_button.clicked.connect(self.send)

        self.layout.addWidget(self.text_display)
        self.layout.addWidget(self.input_line)
        self.layout.addWidget(self.submit_button)
        self.setLayout(self.layout)

    def send(self):
        user_text = self.input_line.text().strip()
        if not user_text:
            return

        self.text_display.append(f"You: {user_text}")
        response = self.task_manager.handle_task(user_text)
        self.text_display.append(f"Caleb: {response}")
        self.input_line.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalebGUI()
    window.show()
    sys.exit(app.exec_())
