import os
import time
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                             QPushButton, QLabel, QCheckBox, QLineEdit, QGroupBox, QSlider)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class VideoTaskThread(QThread):
    result_signal = pyqtSignal(str, bool)
    def __init__(self, video_maker, image_path, options=None):
        super().__init__()
        self.video_maker = video_maker
        self.image_path = image_path
        self.options = options or {}
    def run(self):
        filename = f"jackery_scene_{int(time.time())}.mp4"
        motion_style = self.options.get("motion_style", "Slow Cinematic Zoom")
        success = self.video_maker.generate_motion(self.image_path, motion_style, filename)
        self.result_signal.emit(filename, success)

class VideoVFXWidget(QWidget):
    def __init__(self, parent_main):
        super().__init__()
        self.parent_main = parent_main
        self.layout = QHBoxLayout(self)
        
        self.controls_container = QWidget()
        self.controls = QVBoxLayout(self.controls_container)
        
        # --- HEADER & TOGGLE ---
        header_row = QHBoxLayout()
        header_row.addWidget(QLabel("<b>VIDEO VFX (AnimateDiff)</b>"))
        self.adv_toggle = QCheckBox("Advanced Mode")
        self.adv_toggle.setStyleSheet("color: #e6a822; font-weight: bold;")
        self.adv_toggle.toggled.connect(self.toggle_advanced)
        header_row.addWidget(self.adv_toggle)
        self.controls.addLayout(header_row)
        
        # --- SIMPLE CONTROLS ---
        self.controls.addWidget(QLabel("Source File Name (Start Frame):"))
        self.file_input = QLineEdit()
        self.file_input.setStyleSheet("background-color: #1e1e1e; padding: 5px; color: white;")
        self.controls.addWidget(self.file_input)
        
        self.controls.addWidget(QLabel("Motion Style:"))
        self.motion_picker = QComboBox()
        self.motion_picker.addItems(["Slow Cinematic Zoom", "Pan Left", "Pan Right"])
        self.motion_picker.setStyleSheet("background-color: #1e1e1e; padding: 5px; color: white;")
        self.controls.addWidget(self.motion_picker)
        
        # --- ADVANCED CONTROLS ---
        self.adv_group = QGroupBox("Animation & Rendering Engine")
        self.adv_group.setStyleSheet("QGroupBox { border: 1px solid #444; margin-top: 10px; }")
        adv_layout = QVBoxLayout(self.adv_group)
        
        adv_layout.addWidget(QLabel("Target File Name (End Keyframe):"))
        self.end_frame_input = QLineEdit()
        self.end_frame_input.setPlaceholderText("Optional: e.g. art_end_123.png")
        self.end_frame_input.setStyleSheet("background-color: #1e1e1e; padding: 5px; color: white;")
        adv_layout.addWidget(self.end_frame_input)
        
        adv_layout.addWidget(QLabel("Motion Strength (Stride):"))
        self.stride_slider = QSlider(Qt.Horizontal)
        self.stride_slider.setRange(1, 10)
        self.stride_slider.setValue(4)
        adv_layout.addWidget(self.stride_slider)

        adv_layout.addWidget(QLabel("Frame Count:"))
        self.frames_picker = QComboBox()
        self.frames_picker.addItems(["16 Frames (Fast)", "24 Frames (Smooth)", "32 Frames (Slow)"])
        self.frames_picker.setStyleSheet("background-color: #1e1e1e; padding: 5px; color: white;")
        adv_layout.addWidget(self.frames_picker)
        
        self.upscale_check = QCheckBox("Enable Real-ESRGAN 4K Upscale")
        adv_layout.addWidget(self.upscale_check)
        
        self.controls.addWidget(self.adv_group)
        self.adv_group.hide() # Start hidden
        
        # --- FOOTER ---
        self.generate_btn = QPushButton("RENDER VIDEO")
        self.generate_btn.setStyleSheet("background-color: #b71c1c; color: white; font-weight: bold; padding: 15px;")
        self.generate_btn.clicked.connect(self.generate_video)
        self.controls.addWidget(self.generate_btn)
        
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: #aaaaaa;")
        self.controls.addWidget(self.status_label)
        self.controls.addStretch()
        
        self.controls_container.setFixedWidth(320)
        self.layout.addWidget(self.controls_container)
        
        self.viewer = QLabel("[Check your folder for the MP4 when done]")
        self.viewer.setAlignment(Qt.AlignCenter)
        self.viewer.setStyleSheet("background-color: #0d0d0f; border: 2px dashed #333; font-size: 18px;")
        self.layout.addWidget(self.viewer, 1)

    def toggle_advanced(self, checked):
        if checked:
            self.adv_group.show()
        else:
            self.adv_group.hide()

    def generate_video(self):
        if not hasattr(self.parent_main, 'video_brain') or not self.parent_main.video_brain:
            self.status_label.setText("Error: Video Engine Offline")
            return
        
        image_path = self.file_input.text().strip()
        if not image_path or not os.path.exists(image_path):
            self.status_label.setText(f"Error: Could not find {image_path}")
            return
            
        self.status_label.setText("Rendering... Check terminal.")
        self.generate_btn.setEnabled(False)
        
        opts = {
            "motion_style": self.motion_picker.currentText(),
            "end_frame": self.end_frame_input.text().strip() if self.adv_toggle.isChecked() else "",
            "stride": self.stride_slider.value() if self.adv_toggle.isChecked() else 4,
            "frames": int(self.frames_picker.currentText().split()[0]) if self.adv_toggle.isChecked() else 16,
            "upscale": self.upscale_check.isChecked() if self.adv_toggle.isChecked() else False
        }
        
        self.active_thread = VideoTaskThread(self.parent_main.video_brain, image_path, opts)
        self.active_thread.result_signal.connect(self.on_complete)
        self.active_thread.start()

    def on_complete(self, filename, success):
        self.generate_btn.setEnabled(True)
        if success:
            self.status_label.setText(f"Success! Saved to {filename}")
            self.viewer.setText(f"Done!\n\nOpen {filename}\nin your media player to view.")
        else:
            self.status_label.setText("Error rendering video.")
