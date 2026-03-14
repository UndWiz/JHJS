import sys
import torch
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QCheckBox, QTabWidget, QTextEdit, QLineEdit
from PyQt5.QtCore import QTimer

# --- IMPORT ALL OUR SHINY NEW MODULES ---
try:
    from core.core_vault import CalebVault
    from core.core_hypervisor import CalebHypervisor
    from ui.tabs.tab_settings import SettingsProjectWidget
    from ui.tabs.tab_image_forge import ImageForgeWidget, ImageTaskThread
    from ui.tabs.tab_video_vfx import VideoVFXWidget
    from ui.tabs.tab_audio_lab import AudioLabWidget
    from ui.tabs.tab_training_dojo import TrainingDojoWidget
    from ui.tabs.tab_advanced_builder import AdvancedBuilderWidget, AITaskThread
except ImportError as e:
    print(f"[!] Modular import failed: {e}")
    sys.exit(1)

# Import the Brains
try: from image_maker import CalebImageMaker
except ImportError: CalebImageMaker = None

try: from video_maker import CalebVideoMaker
except ImportError: CalebVideoMaker = None

try: from audio_maker import CalebAudioMaker
except ImportError: CalebAudioMaker = None

class JackeryGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jack Hole Jackery Studios - Master Director Mode")
        self.setGeometry(50, 50, 1600, 950)
        self.setStyleSheet("background-color: #0d0d0f; color: #e6e6eb;")

        # Initialize Core Systems
        self.vault = CalebVault()
        self.hypervisor = CalebHypervisor()

        # Initialize Brains
        self.image_brain = CalebImageMaker() if CalebImageMaker else None
        self.video_brain = CalebVideoMaker() if CalebVideoMaker else None
        self.audio_brain = CalebAudioMaker() if CalebAudioMaker else None

        # Main Layout setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Header
        header_area = QHBoxLayout()
        studio_lbl = QLabel("Jack Hole Jackery Studios")
        studio_lbl.setStyleSheet("font-size: 14pt; font-weight: bold; color: #00ff00;")
        
        self.vram_lbl = QLabel("VRAM: --/--GB | Engine: None")
        self.vram_lbl.setStyleSheet("color: #00ffff; font-weight: bold; margin-right: 20px;")
        
        self.adv_toggle = QCheckBox("ADVANCED NLE BUILDER")
        self.adv_toggle.setStyleSheet("color: #e6a822;")
        self.adv_toggle.toggled.connect(self.toggle_builder)
        
        header_area.addWidget(studio_lbl)
        header_area.addStretch()
        header_area.addWidget(self.vram_lbl)
        header_area.addWidget(self.adv_toggle)
        self.main_layout.addLayout(header_area)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_change)
        self.main_layout.addWidget(self.tabs)

        # The Director's Hub (Simple View)
        self.caleb_hub_tab = QWidget()
        self.hub_layout = QVBoxLayout(self.caleb_hub_tab)
        
        self.simple_view = QWidget()
        sv_layout = QHBoxLayout(self.simple_view)
        sv_layout.setContentsMargins(0,0,0,0)
        
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("background-color: #1a1a1e; border-right: 1px solid #333;")
        sidebar_layout = QVBoxLayout(sidebar)
        new_chat_btn = QPushButton("+ New Chat")
        new_chat_btn.setStyleSheet("background-color: #2a2a30; padding: 12px; border-radius: 6px; font-weight: bold; color: #e6e6eb;")
        sidebar_layout.addWidget(new_chat_btn)
        sidebar_layout.addStretch()
        
        main_chat_area = QWidget()
        main_chat_layout = QVBoxLayout(main_chat_area)
        self.simple_chat = QTextEdit()
        self.simple_chat.setReadOnly(True)
        self.simple_chat.setStyleSheet("background-color: #121214; border: none; padding: 20px; font-size: 14px;")
        self.simple_chat.append("<b>[SYSTEM]</b> JackHole. All modules have been decoupled. We are running a fully scalable Master Architecture.")
        
        input_container = QHBoxLayout()
        self.simple_input = QLineEdit()
        self.simple_input.setPlaceholderText("Message CALEB or tell him to draw...")
        self.simple_input.setStyleSheet("background-color: #2a2a30; padding: 15px; border-radius: 10px; border: 1px solid #444; font-size: 14px;")
        self.simple_send = QPushButton("Send")
        self.simple_send.setStyleSheet("background-color: #5078c8; padding: 15px 25px; border-radius: 10px; font-weight: bold;")
        
        self.simple_send.clicked.connect(self.handle_simple_input)
        self.simple_input.returnPressed.connect(self.handle_simple_input)

        input_container.addWidget(self.simple_input)
        input_container.addWidget(self.simple_send)
        
        main_chat_layout.addWidget(self.simple_chat)
        main_chat_layout.addLayout(input_container)
        
        sv_layout.addWidget(sidebar)
        sv_layout.addWidget(main_chat_area)

        # Initialize Advanced Builder
        self.advanced_builder = AdvancedBuilderWidget(self)
        
        self.hub_layout.addWidget(self.simple_view)
        self.hub_layout.addWidget(self.advanced_builder)
        self.advanced_builder.hide()

        # Add all Modular Tabs
        self.tabs.addTab(self.caleb_hub_tab, "CALEB Hub")
        self.tabs.addTab(ImageForgeWidget(self), "Image Forge")  
        self.tabs.addTab(VideoVFXWidget(self), "Video Motion VFX")
        self.tabs.addTab(AudioLabWidget(self), "Audio Lab") 
        self.tabs.addTab(TrainingDojoWidget(self), "Training Dojo (Art)")
        self.tabs.addTab(SettingsProjectWidget(self), "Settings & Projects")

        # Start VRAM monitor timer
        self.vram_timer = QTimer()
        self.vram_timer.timeout.connect(self.update_vram_display)
        self.vram_timer.start(2000)

    def on_tab_change(self, index):
        tab_name = self.tabs.tabText(index)
        if "Image" in tab_name:
            self.hypervisor.wake_engine("Image Engine (SDXL)")
        elif "Video" in tab_name:
            self.hypervisor.wake_engine("Video Engine (AnimateDiff)")
        elif "Audio" in tab_name:
            self.hypervisor.wake_engine("Audio Engine (RVC/Wav2Lip)")
        elif "Training" in tab_name:
            self.hypervisor.wake_engine("Training Engine (LoRA)")
        else:
            self.hypervisor.wake_engine("CALEB Core (LLM)")

    def update_vram_display(self):
        engine = getattr(self.hypervisor, 'active_engine', 'None')
        try:
            if hasattr(torch, 'xpu') and torch.xpu.is_available():
                used = torch.xpu.memory_allocated() / (1024**3)
                self.vram_lbl.setText(f"VRAM: {used:.1f}/16GB | Engine: {engine}")
                if used > 13: self.vram_lbl.setStyleSheet("color: red; font-weight: bold;")
                else: self.vram_lbl.setStyleSheet("color: #00ffff; font-weight: bold;")
                return
        except:
            pass
        self.vram_lbl.setText(f"VRAM: N/A | Engine: {engine}")

    def handle_simple_input(self):
        text = self.simple_input.text().strip()
        if not text: return
        self.simple_input.clear()
        self.simple_chat.append(f"<span style='color:#00ff00;'><b>You:</b></span> {text}<br>")
        
        if "draw" in text.lower():
            if not self.image_brain:
                self.simple_chat.append("<span style='color:#ff0000;'><b>CALEB:</b></span> My visual brain ain't loaded right.<br>")
                return
            prompt = text.lower().replace("draw", "").strip()
            self.simple_chat.append(f"<span style='color:#00ffff;'><b>CALEB:</b></span> I'm on it. Sending '{prompt}' to the GPU...<br>")
            self.active_image_thread = ImageTaskThread(self.image_brain, prompt)
            self.active_image_thread.result_signal.connect(self.on_simple_image_complete)
            self.active_image_thread.start()
        else:
            self.simple_chat.append(f"<span style='color:#aaaaaa;'><i>Thinking...</i></span><br>")
            if hasattr(self.advanced_builder, 'controller') and self.advanced_builder.controller:
                self.active_text_thread = AITaskThread(self.advanced_builder.controller, text)
                self.active_text_thread.result_signal.connect(self.on_simple_text_complete)
                self.active_text_thread.start()
            else:
                self.simple_chat.append("<span style='color:#ff0000;'><b>CALEB:</b></span> The logic controller ain't hooked up right now.<br>")

    def on_simple_image_complete(self, prompt, filename):
        self.simple_chat.append(f"<span style='color:#ff00ff;'><b>CALEB (Visual):</b></span> Got it. Saved it as {filename} for ya.<br>")

    def on_simple_text_complete(self, raw_ai, execution_results):
        safe_ai_text = raw_ai.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
        self.simple_chat.append(f"<span style='color:#00ffff;'><b>CALEB:</b></span><br>{safe_ai_text}<br>")

    def toggle_builder(self, checked):
        if checked:
            self.simple_view.hide()
            self.advanced_builder.show()
        else:
            self.advanced_builder.hide()
            self.simple_view.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JackeryGUI()
    window.show()
    sys.exit(app.exec_())
