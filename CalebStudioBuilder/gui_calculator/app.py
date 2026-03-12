import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QLineEdit, QPushButton

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JHJS Test Calculator")
        self.setStyleSheet("background-color: #2b2b2b; color: #ffffff; font-size: 18px;")
        self.resize(300, 400)
        
        layout = QVBoxLayout()
        
        self.display = QLineEdit()
        self.display.setStyleSheet("background-color: #1e1e1e; padding: 15px; font-size: 24px; border: 1px solid #555;")
        self.display.setReadOnly(True)
        layout.addWidget(self.display)
        
        grid = QGridLayout()
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            'C', '0', '=', '+'
        ]
        
        row = 0
        col = 0
        for text in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("background-color: #3c3c3c; padding: 20px; border-radius: 5px;")
            btn.clicked.connect(lambda checked, t=text: self.on_click(t))
            grid.addWidget(btn, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1
                
        layout.addLayout(grid)
        self.setLayout(layout)

    def on_click(self, char):
        if char == 'C':
            self.display.clear()
        elif char == '=':
            try:
                # Safely evaluate the math string
                result = str(eval(self.display.text()))
                self.display.setText(result)
            except Exception:
                self.display.setText("Error")
        else:
            self.display.setText(self.display.text() + char)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())
