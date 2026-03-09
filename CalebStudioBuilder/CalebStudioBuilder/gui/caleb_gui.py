# gui/caleb_gui.py

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton

# FIXED IMPORT: match actual class name in core/caleb_task_manager.py
from core.caleb_task_manager import TaskManager  # <-- was CalebTaskManager

from core.caleb_initializer import CalebInitializer
from core.caleb_builder import CalebBuilder
from core.memory_manager import MemoryManager
from core.file_manager import FileManager
from core.dependency_manager import DependencyManager

class CalebGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        # initialize Caleb components
        self.memory_manager = MemoryManager()
        self.file_manager = FileManager()
        self.dependency_manager = DependencyManager()
        self.task_manager = TaskManager()  # <-- updated to match class
        self.caleb_initializer = CalebInitializer()
        self.caleb_builder = CalebBuilder()

    def init_ui(self):
        self.setWindowTitle("Caleb Studio Builder")
        self.layout = QVBoxLayout()
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.input_line = QLineEdit()
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.handle_input)

        self.layout.addWidget(self.chat_history)
        self.layout.addWidget(self.input_line)
        self.layout.addWidget(self.send_button)
        self.setLayout(self.layout)

    def handle_input(self):
        user_input = self.input_line.text()
        self.chat_history.append(f"User: {user_input}")
        response = self.task_manager.handle_task(user_input)
        self.chat_history.append(f"Caleb: {response}")
        self.input_line.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = CalebGUI()
    gui.show()
    sys.exit(app.exec_())
