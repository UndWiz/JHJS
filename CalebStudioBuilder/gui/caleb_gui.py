# caleb_gui.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QLabel, QComboBox, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer
from core.caleb_task_manager import CalebTaskManager
from core.memory_manager import MemoryManager

class CalebGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Caleb Studio Builder - Chat Interface")
        self.setGeometry(200, 200, 800, 600)

        # Core backend
        self.task_manager = CalebTaskManager()
        self.memory_manager = MemoryManager()

        # Layouts
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.create_model_selector()
        self.create_chat_display()
        self.create_input_area()
        self.create_memory_buttons()

    def create_model_selector(self):
        layout = QHBoxLayout()
        label = QLabel("Active Model:")
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(["Caleb-Creative", "Caleb-Technical", "Caleb-Audio/Video"])
        layout.addWidget(label)
        layout.addWidget(self.model_dropdown)
        self.main_layout.addLayout(layout)

    def create_chat_display(self):
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.main_layout.addWidget(self.chat_display)

    def create_input_area(self):
        layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your command or question here...")
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.input_field)
        layout.addWidget(self.send_button)
        self.main_layout.addLayout(layout)

    def create_memory_buttons(self):
        layout = QHBoxLayout()
        self.save_button = QPushButton("Save to Memory")
        self.save_button.clicked.connect(self.save_memory)
        self.forget_button = QPushButton("Forget Selected")
        self.forget_button.clicked.connect(self.forget_memory)
        self.memory_list = QListWidget()
        layout.addWidget(self.save_button)
        layout.addWidget(self.forget_button)
        layout.addWidget(self.memory_list)
        self.main_layout.addLayout(layout)
        self.refresh_memory_list()

    def send_message(self):
        user_input = self.input_field.text().strip()
        if not user_input:
            return
        self.chat_display.append(f"<b>You:</b> {user_input}")

        # Send to CalebTaskManager
        model = self.model_dropdown.currentText()
        response = self.task_manager.process_command(user_input, model)

        self.chat_display.append(f"<b>{model}:</b> {response}")
        self.input_field.clear()

    def save_memory(self):
        text = self.input_field.text().strip()
        if text:
            self.memory_manager.save(text)
            self.refresh_memory_list()
            self.input_field.clear()

    def forget_memory(self):
        selected_items = self.memory_list.selectedItems()
        for item in selected_items:
            self.memory_manager.delete(item.text())
        self.refresh_memory_list()

    def refresh_memory_list(self):
        self.memory_list.clear()
        for entry in self.memory_manager.get_all():
            self.memory_list.addItem(QListWidgetItem(entry))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = CalebGUI()
    gui.show()
    sys.exit(app.exec())
