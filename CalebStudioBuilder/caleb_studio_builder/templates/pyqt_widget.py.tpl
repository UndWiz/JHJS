from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class {{CLASS_NAME}}(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.label = QLabel("{{LABEL_TEXT}}")
        layout.addWidget(self.label)
