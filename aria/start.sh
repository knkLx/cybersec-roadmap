#!/bin/bash
export PATH="$HOME/.miniforge/bin:$PATH"
export LD_LIBRARY_PATH="$HOME/.local/lib/ollama:$LD_LIBRARY_PATH"

# Start Ollama if not running
if ! pgrep -x ollama > /dev/null; then
    echo "[*] Starting Ollama..."
    setsid ollama serve &>/tmp/ollama.log &
    sleep 3
fi

echo "[*] Starting ARIA..."
cd "$(dirname "$0")"
python3 app.py
