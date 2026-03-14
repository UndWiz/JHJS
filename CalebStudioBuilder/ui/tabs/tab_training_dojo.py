import os
import time
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QProgressBar, QTextEdit, QGroupBox, QFileDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class TrainingTaskThread(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    done_signal = pyqtSignal(bool)
    
    def __init__(self, dataset_path, lora_name):
        super().__init__()
        self.dataset_path = dataset_path
        self.lora_name = lora_name
        
    def run(self):
        self.log_signal.emit(f"[SYS] Starting LoRA Training for: {self.lora_name}")
        self.log_signal.emit(f"[SYS] Scanning dataset at: {self.dataset_path}")
        
        # Simulated training loop for UI wiring
        for i in range(1, 101):
            time.sleep(0.1) # Simulate heavy GPU processing
            if i % 10 == 0:
                self.log_signal.emit(f"[TRAIN] Epoch {i//10}/10 completed. Loss: 0.1{99-i}")
            self.progress_signal.emit(i)
            
        self.log_signal.emit(f"[SUCCESS] LoRA {self.lora_name}.safetensors saved to vault!")
        self.done_signal.emit(True)

class TrainingDojoWidget(QWidget):
    def __init__(self, parent_main):
        super().__init__()
        self.parent_main = parent_main
        self.layout = QVBoxLayout(self)
        
        header_row = QHBoxLayout()
        header_row.addWidget(QLabel("<b>THE TRAINING DOJO (LoRA Maker)</b>"))
        header_row.addStretch()
        self.layout.addLayout(header_row)

        # Dataset Prep Group
        self.data_group = QGroupBox("1. Dataset Preparation")
        self.data_group.setStyleSheet("QGroupBox { border: 1px solid #444; margin-top: 10px; }")
        data_layout = QVBoxLayout(self.data_group)
        
        data_layout.addWidget(QLabel("Folder containing your art:"))
        row1 = QHBoxLayout()
        self.path_in = QLineEdit()
        self.path_in.setPlaceholderText("/path/to/your/custom/art/folder")
        self.path_in.setStyleSheet("background-color: #1e1e1e; padding: 5px; color: white;")
        row1.addWidget(self.path_in)
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_folder)
        row1.addWidget(self.browse_btn)
        data_layout.addLayout(row1)
        
        self.caption_btn = QPushButton("Auto-Caption Art (BLIP Vision)")
        self.caption_btn.setStyleSheet("background-color: #2a2a30; font-weight: bold; padding: 8px;")
        data_layout.addWidget(self.caption_btn)
        self.layout.addWidget(self.data_group)

        # Training Group
        self.train_group = QGroupBox("2. LoRA Training Engine")
        self.train_group.setStyleSheet("QGroupBox { border: 1px solid #444; margin-top: 10px; }")
        train_layout = QVBoxLayout(self.train_group)
        
        train_layout.addWidget(QLabel("Name your custom Art Style (e.g., Jesse_Style):"))
        self.lora_name_in = QLineEdit()
        self.lora_name_in.setStyleSheet("background-color: #1e1e1e; padding: 5px; color: white;")
        train_layout.addWidget(self.lora_name_in)
        
        self.train_btn = QPushButton("FORGE CUSTOM LORA")
        self.train_btn.setStyleSheet("background-color: #ff5500; color: white; font-weight: bold; padding: 15px;")
        self.train_btn.clicked.connect(self.start_training)
        train_layout.addWidget(self.train_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        train_layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.train_group)

        # Live Terminal
        self.layout.addWidget(QLabel("<b>Live Training Logs:</b>"))
        self.term_out = QTextEdit()
        self.term_out.setReadOnly(True)
        self.term_out.setStyleSheet("background-color: #0d0d0f; color: #00ff00; font-family: monospace;")
        self.layout.addWidget(self.term_out, 1)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Art Dataset Folder")
        if folder:
            self.path_in.setText(folder)

    def start_training(self):
        dataset = self.path_in.text().strip()
        name = self.lora_name_in.text().strip()
        
        if not dataset or not name:
            self.term_out.append("[!] Error: You need to select a dataset folder and name your style.")
            return
            
        self.train_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.term_out.append(f"--- INITIALIZING TRAINING SEQUENCE: {name} ---")
        
        self.thread = TrainingTaskThread(dataset, name)
        self.thread.log_signal.connect(self.term_out.append)
        self.thread.progress_signal.connect(self.progress_bar.setValue)
        self.thread.done_signal.connect(lambda: self.train_btn.setEnabled(True))
        self.thread.start()
