import os
import time
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QComboBox, 
                             QPushButton, QLabel, QCheckBox, QScrollArea, QSlider, QLineEdit, QGroupBox, QFileDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap

class ImageTaskThread(QThread):
    result_signal = pyqtSignal(str, str)
    def __init__(self, image_maker, prompt, options=None):
        super().__init__()
        self.image_maker = image_maker
        self.prompt = prompt
        self.options = options or {}
    def run(self):
        filename = f"jackery_art_{int(time.time())}.png"
        self.image_maker.draw_advanced(self.prompt, filename=filename, options=self.options)
        self.result_signal.emit(self.prompt, filename)

class ImageForgeWidget(QWidget):
    def __init__(self, parent_main):
        super().__init__()
        self.parent_main = parent_main
        self.layout = QHBoxLayout(self)

        self.controls_container = QWidget()
        self.controls_layout = QVBoxLayout(self.controls_container)
        
        # --- HEADER & TOGGLE ---
        header_row = QHBoxLayout()
        header_row.addWidget(QLabel("<b>IMAGE FORGE (SDXL)</b>"))
        self.adv_toggle = QCheckBox("Advanced Mode")
        self.adv_toggle.setStyleSheet("color: #e6a822; font-weight: bold;")
        self.adv_toggle.toggled.connect(self.toggle_advanced)
        header_row.addWidget(self.adv_toggle)
        self.controls_layout.addLayout(header_row)

        # --- SIMPLE CONTROLS (Always Visible) ---
        self.controls_layout.addWidget(QLabel("Art Model:"))
        self.model_picker = QComboBox()
        self.model_picker.addItems(["SDXL Base 1.0", "Cartoon Mayhem (SD 1.5)"])
        self.controls_layout.addWidget(self.model_picker)

        self.controls_layout.addWidget(QLabel("Aspect Ratio:"))
        self.ratio_picker = QComboBox()
        self.ratio_picker.addItems(["16:9 (Widescreen)", "1:1 (Square)", "9:16 (Vertical)"])
        self.controls_layout.addWidget(self.ratio_picker)

        self.controls_layout.addWidget(QLabel("Prompt:"))
        self.prompt_input = QTextEdit()
        self.prompt_input.setMaximumHeight(80)
        self.controls_layout.addWidget(self.prompt_input)

        # --- ADVANCED CONTROLS (Hidden by default) ---
        self.adv_group = QGroupBox("Surgical Controls")
        self.adv_group.setStyleSheet("QGroupBox { border: 1px solid #444; margin-top: 10px; }")
        adv_layout = QVBoxLayout(self.adv_group)

        adv_layout.addWidget(QLabel("Character DNA Injector:"))
        self.dna_picker = QComboBox()
        self.dna_picker.addItems(["None (Free Render)", "Load from Vault..."])
        adv_layout.addWidget(self.dna_picker)

        adv_layout.addWidget(QLabel("Negative Prompt:"))
        self.neg_prompt = QTextEdit()
        self.neg_prompt.setMaximumHeight(50)
        adv_layout.addWidget(self.neg_prompt)

        adv_layout.addWidget(QLabel("Detail Steps (10-50):"))
        self.steps_slider = QSlider(Qt.Horizontal)
        self.steps_slider.setRange(10, 50)
        self.steps_slider.setValue(25)
        adv_layout.addWidget(self.steps_slider)

        adv_layout.addWidget(QLabel("CFG Scale (Prompt Strictness):"))
        self.cfg_slider = QSlider(Qt.Horizontal)
        self.cfg_slider.setRange(1, 15)
        self.cfg_slider.setValue(7)
        adv_layout.addWidget(self.cfg_slider)

        adv_layout.addWidget(QLabel("Manual Seed (0 = Random):"))
        self.seed_input = QLineEdit("0")
        adv_layout.addWidget(self.seed_input)

        self.upscale_check = QCheckBox("Enable Real-ESRGAN 4K Upscale")
        adv_layout.addWidget(self.upscale_check)

        self.controls_layout.addWidget(self.adv_group)
        self.adv_group.hide() # Start hidden

        # --- FOOTER ---
        self.generate_btn = QPushButton("FORGE IMAGE")
        self.generate_btn.setStyleSheet("background-color: #e6a822; color: black; font-weight: bold; padding: 15px;")
        self.generate_btn.clicked.connect(self.generate)
        self.controls_layout.addWidget(self.generate_btn)

        self.status_lbl = QLabel("Ready")
        self.controls_layout.addWidget(self.status_lbl)
        self.controls_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(self.controls_container)
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(350)
        scroll.setStyleSheet("border: none;")

        self.viewer = QLabel("Art Preview Area")
        self.viewer.setAlignment(Qt.AlignCenter)
        self.viewer.setStyleSheet("background-color: #000; border: 1px dashed #333;")

        self.layout.addWidget(scroll)
        self.layout.addWidget(self.viewer, 1)

    def toggle_advanced(self, checked):
        if checked:
            self.adv_group.show()
        else:
            self.adv_group.hide()

    def generate(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt or not self.parent_main.image_brain: 
            self.status_lbl.setText("Error: Brain offline or empty prompt.")
            return
            
        self.status_lbl.setText("Forging... Check terminal.")
        self.generate_btn.setEnabled(False)
        
        opts = {
            "model": self.model_picker.currentText(),
            "aspect_ratio": self.ratio_picker.currentText(),
            "negative_prompt": self.neg_prompt.toPlainText().strip() if self.adv_toggle.isChecked() else "",
            "steps": self.steps_slider.value() if self.adv_toggle.isChecked() else 25,
            "cfg": self.cfg_slider.value() if self.adv_toggle.isChecked() else 7,
            "seed": int(self.seed_input.text()) if self.adv_toggle.isChecked() and self.seed_input.text().isdigit() else 0,
            "upscale": self.upscale_check.isChecked() if self.adv_toggle.isChecked() else False
        }
        
        self.thread = ImageTaskThread(self.parent_main.image_brain, prompt, opts)
        self.thread.result_signal.connect(self.on_done)
        self.thread.start()

    def on_done(self, prompt, filename):
        self.status_lbl.setText(f"Saved: {filename}")
        self.generate_btn.setEnabled(True)
        pix = QPixmap(filename)
        self.viewer.setPixmap(pix.scaled(self.viewer.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
