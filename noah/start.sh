#!/bin/bash
# ============================================
#  NOAH — Startup Script
#  Arranca: Ollama + NOAH + Dashboard
#  Ejecutar: bash ~/noah/start.sh
# ============================================

export PATH="$HOME/.miniforge/bin:$HOME/.local/bin:$PATH"
export LD_LIBRARY_PATH="$HOME/.local/lib:$HOME/.local/bin:/tmp/piper:$LD_LIBRARY_PATH"
export ESPEAK_DATA_PATH="/usr/lib/x86_64-linux-gnu/espeak-ng-data"

NOAH_DIR="$HOME/noah"
LOG="/tmp/noah.log"

echo ""
echo "  ╔══════════════════════════════════╗"
echo "  ║     NOAH — AI Companion          ║"
echo "  ║     Starting all systems...      ║"
echo "  ╚══════════════════════════════════╝"
echo ""

# Kill previous instances
echo "[1/4] Cleaning previous processes..."
pkill -9 -f "noah/app.py" 2>/dev/null
sleep 1
echo "  ✓ Clean"

# Start Ollama
echo "[2/4] Starting Ollama..."
if pgrep -x ollama > /dev/null; then
    echo "  ✓ Ollama already running"
else
    setsid ollama serve &>/tmp/ollama.log &
    sleep 3
    echo "  ✓ Ollama started"
fi

# Preload model
echo "[3/4] Preloading qwen2.5:1.5b..."
curl -s http://localhost:11434/api/generate -d '{"model":"qwen2.5:1.5b","prompt":"test","stream":false}' > /dev/null 2>&1 &
sleep 2
echo "  ✓ Model ready"

# Start NOAH
echo "[4/4] Starting NOAH on http://localhost:7861..."
cd "$NOAH_DIR"
setsid python3 app.py > "$LOG" 2>&1 &
NOAH_PID=$!
sleep 3

# Verify
echo ""
echo "  ╔══════════════════════════════════╗"
echo "  ║     STATUS                       ║"
echo "  ╚══════════════════════════════════╝"

if ss -tlnp | grep -q "7861"; then
    echo "  ✓ NOAH Chat:    http://localhost:7861      (PID: $NOAH_PID)"
else
    echo "  ✗ NOAH Chat:    FAILED — check $LOG"
fi

if ss -tlnp | grep -q "11434"; then
    echo "  ✓ Ollama:       http://localhost:11434"
else
    echo "  ✗ Ollama:       FAILED"
fi

if pgrep -x ollama > /dev/null; then
    echo "  ✓ Model:        qwen2.5:1.5b loaded"
else
    echo "  ✗ Model:        not loaded"
fi

echo ""
echo "  Dashboard: http://localhost:7861/dashboard"
echo "  Chat:      http://localhost:7861"
echo ""
echo "  To stop:   pkill -9 -f 'noah/app.py'"
echo ""
