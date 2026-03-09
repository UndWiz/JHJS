# gui/caleb_gui.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
from core.memory_manager import MemoryManager
from core.dependency_manager import DependencyManager
from core.caleb_task_manager import CalebTaskManager

class CalebGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Caleb Studio Builder")
        self.setGeometry(100, 100, 800, 600)

        # Initialize core modules
        self.memory_manager = MemoryManager()
        self.dependency_manager = DependencyManager(self.memory_manager)
        self.task_manager = CalebTaskManager()

        # GUI components
        self.layout = QVBoxLayout()
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.input_line = QLineEdit()
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.process_input)

        # Add components to layout
        self.layout.addWidget(self.output_area)
        self.layout.addWidget(self.input_line)
        self.layout.addWidget(self.submit_button)
        self.setLayout(self.layout)

    def process_input(self):
        user_input = self.input_line.text().strip()
        if not user_input:
            return
        self.output_area.append(f"You: {user_input}")

        # Process input via task manager (basic example)
        response = self.task_manager.handle_task(user_input, self.memory_manager, self.dependency_manager)
        self.output_area.append(f"Caleb: {response}")

        # Clear input line
        self.input_line.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = CalebGUI()
    gui.show()
    sys.exit(app.exec_())
