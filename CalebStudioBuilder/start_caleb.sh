#!/bin/bash
PROJECT_DIR="${HOME}/CalebStudioBuilder"
echo "[*] Initializing CALEB Environment at $PROJECT_DIR..."
cd "$PROJECT_DIR"

if [ ! -d "venv" ]; then
    echo "[!] Critical Error: Python virtual environment 'venv' not found."
    exit 1
fi

source venv/bin/activate

echo "[*] Checking local Ollama endpoint..."
if curl -s -f -m 2 http://127.0.0.1:11434/api/tags > /dev/null; then
    echo "[+] Local inference engine detected."
else
    echo "[!] Ollama is not running. Booting inference engine in the background..."
    ollama serve > /dev/null 2>&1 &
    
    # Wait up to 10 seconds for the engine to wake up
    for i in {1..10}; do
        if curl -s -f -m 2 http://127.0.0.1:11434/api/tags > /dev/null; then
            echo "[+] Engine online."
            break
        fi
        sleep 1
    done
fi

echo "[+] Launching CALEB Studio GUI..."
python3 main.py
