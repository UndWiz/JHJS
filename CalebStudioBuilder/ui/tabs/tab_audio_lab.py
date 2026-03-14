import os
import time
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QComboBox, 
                             QPushButton, QLabel, QCheckBox, QLineEdit, QGroupBox, QSlider)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class AudioTaskThread(QThread):
    result_signal = pyqtSignal(str)
    def __init__(self, audio_maker, text, voice_type, filename, options=None):
        super().__init__()
        self.audio_maker = audio_maker
        self.text = text
        self.voice_type = voice_type
        self.filename = filename
        self.options = options or {}
        
    def run(self):
        # We pass the advanced options down if the engine supports it
        self.audio_maker.generate_voice(self.text, self.voice_type, self.filename)
        self.result_signal.emit(self.filename)

class AudioLabWidget(QWidget):
    def __init__(self, parent_main):
        super().__init__()
        self.parent_main = parent_main
        self.layout = QHBoxLayout(self)
        
        self.controls_container = QWidget()
        self.controls = QVBoxLayout(self.controls_container)
        
        # --- HEADER & TOGGLE ---
        header_row = QHBoxLayout()
        header_row.addWidget(QLabel("<b>AUDIO LAB (TTS & RVC)</b>"))
        self.adv_toggle = QCheckBox("Advanced Mode")
        self.adv_toggle.setStyleSheet("color: #e6a822; font-weight: bold;")
        self.adv_toggle.toggled.connect(self.toggle_advanced)
        header_row.addWidget(self.adv_toggle)
        self.controls.addLayout(header_row)
        
        # --- SIMPLE CONTROLS ---
        self.controls.addWidget(QLabel("Script / Dialogue:"))
        self.script_input = QTextEdit()
        self.script_input.setStyleSheet("background-color: #1e1e1e; padding: 5px; color: white;")
        self.controls.addWidget(self.script_input)
        
        self.controls.addWidget(QLabel("Standard Voice Type:"))
        self.voice_picker = QComboBox()
        self.voice_picker.addItems(["Standard Male", "Standard Female", "Robot / Synthesizer"])
        self.voice_picker.setStyleSheet("background-color: #1e1e1e; padding: 5px; color: white;")
        self.controls.addWidget(self.voice_picker)
        
        # --- ADVANCED CONTROLS ---
        self.adv_group = QGroupBox("RVC Cloning & Wav2Lip Syncing")
        self.adv_group.setStyleSheet("QGroupBox { border: 1px solid #444; margin-top: 10px; }")
        adv_layout = QVBoxLayout(self.adv_group)
        
        adv_layout.addWidget(QLabel("<b>RVC Voice Clone Override:</b>"))
        self.rvc_input = QLineEdit()
        self.rvc_input.setPlaceholderText("Path to .pth voice model (Optional)")
        self.rvc_input.setStyleSheet("background-color: #1e1e1e; padding: 5px; color: white;")
        adv_layout.addWidget(self.rvc_input)
        
        adv_layout.addWidget(QLabel("Pitch Shift (For RVC):"))
        self.pitch_slider = QSlider(Qt.Horizontal)
        self.pitch_slider.setRange(-12, 12)
        self.pitch_slider.setValue(0)
        adv_layout.addWidget(self.pitch_slider)

        adv_layout.addWidget(QLabel("<hr><b>Wav2Lip Target Video:</b>"))
        self.video_sync_input = QLineEdit()
        self.video_sync_input.setPlaceholderText("Path to MP4 to lip-sync (Optional)")
        self.video_sync_input.setStyleSheet("background-color: #1e1e1e; padding: 5px; color: white;")
        adv_layout.addWidget(self.video_sync_input)

        adv_layout.addWidget(QLabel("<hr><b>Neural Soundstage:</b>"))
        self.acoustics_picker = QComboBox()
        self.acoustics_picker.addItems(["Studio (Dry)", "Small Room", "Large Hall", "Outdoor / Muffled"])
        self.acoustics_picker.setStyleSheet("background-color: #1e1e1e; padding: 5px; color: white;")
        adv_layout.addWidget(self.acoustics_picker)

        self.controls.addWidget(self.adv_group)
        self.adv_group.hide() # Start hidden
        
        # --- FOOTER ---
        self.generate_btn = QPushButton("GENERATE AUDIO")
        self.generate_btn.setStyleSheet("background-color: #1976d2; color: white; font-weight: bold; padding: 15px;")
        self.generate_btn.clicked.connect(self.generate_audio)
        self.controls.addWidget(self.generate_btn)
        
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: #aaaaaa;")
        self.controls.addWidget(self.status_label)
        self.controls.addStretch()
        
        self.controls_container.setFixedWidth(320)
        self.layout.addWidget(self.controls_container)
        
        self.viewer = QLabel("[Check your folder for the MP3/MP4 when done]")
        self.viewer.setAlignment(Qt.AlignCenter)
        self.viewer.setStyleSheet("background-color: #0d0d0f; border: 2px dashed #333; font-size: 18px;")
        self.layout.addWidget(self.viewer, 1)

    def toggle_advanced(self, checked):
        if checked:
            self.adv_group.show()
        else:
            self.adv_group.hide()

    def generate_audio(self):
        if not hasattr(self.parent_main, 'audio_brain') or not self.parent_main.audio_brain:
            self.status_label.setText("Error: Audio Engine Offline")
            return
            
        script = self.script_input.toPlainText().strip()
        if not script: return
        
        voice_type = self.voice_picker.currentText()
        filename = f"jackery_voice_{int(time.time())}.mp3"
        
        self.status_label.setText("Recording... Check terminal.")
        self.generate_btn.setEnabled(False)
        
        opts = {
            "rvc_model": self.rvc_input.text().strip() if self.adv_toggle.isChecked() else "",
            "pitch": self.pitch_slider.value() if self.adv_toggle.isChecked() else 0,
            "video_sync": self.video_sync_input.text().strip() if self.adv_toggle.isChecked() else "",
            "acoustics": self.acoustics_picker.currentText() if self.adv_toggle.isChecked() else "Studio (Dry)"
        }
        
        self.active_thread = AudioTaskThread(self.parent_main.audio_brain, script, voice_type, filename, options=opts)
        self.active_thread.result_signal.connect(self.on_complete)
        self.active_thread.start()

    def on_complete(self, filename):
        self.generate_btn.setEnabled(True)
        self.status_label.setText(f"Success! Saved to {filename}")
        self.viewer.setText(f"Done!\n\nOpen {filename}\nin your media player to listen.")
