#!/bin/bash
# CALEB Master Launcher

PROJECT_DIR="${HOME}/CalebStudioBuilder"
echo "[*] Initializing CALEB Environment at $PROJECT_DIR..."
cd "$PROJECT_DIR"

if [ ! -d "venv" ]; then
    echo "[!] Critical Error: Python virtual environment 'venv' not found."
    echo "    Please run the initial Phase 1 bootstrap script."
    exit 1
fi

source venv/bin/activate

# Optional: Verify Ollama is responsive before launching the GUI
echo "[*] Pinging local Ollama endpoint..."
if curl -s -f -m 2 http://127.0.0.1:11434/api/tags > /dev/null; then
    echo "[+] Local inference engine detected."
else
    echo "[!] Warning: Ollama does not appear to be running on 127.0.0.1:11434."
    echo "    CALEB will launch, but AI inference will fail until the engine is started."
fi

echo "[+] Launching CALEB Studio GUI..."
python3 main.py
