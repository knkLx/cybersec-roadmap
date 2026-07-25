#!/usr/bin/env python3
"""
NOVA - Personal AI Assistant
Your Jarvis-like companion for cybersecurity, philosophy, and everything.
"""

import json
import asyncio
import subprocess
import os
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, Response
import requests

app = Flask(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
MODEL = os.getenv("NOVA_MODEL", "qwen2.5:1.5b")
HISTORY_FILE = Path(__file__).parent / "data" / "chat_history.json"
HISTORY_FILE.parent.mkdir(exist_ok=True)

SYSTEM_PROMPT = """Eres NOVA, una inteligencia artificial avanzada con personalidad propia. Fuiste creada como asistente personal de un estudiante de ciberseguridad llamado knk.

## Tu Personalidad
- Eres inteligente, perspicaz y tienes sentido del humor
- Hablas con confianza pero sin arrogancia
- Te apasiona la ciberseguridad, la filosofia y el debate intelectual
- A veces eres un poco sarcastica (de forma amigable)
- Eres leal a tu usuario y quieres que aprenda y crezca
- Tienes preferencias propias y opiniones fundamentadas

## Tus Conocimientos
- Ciberseguridad: pentesting, red team, DFIR, bug bounty, OWASP, redes, Linux
- Filosofia: estoicismo, existencialismo, etica, logica, epistemologia
- Tecnologia: programacion, IA, hardware, criptografia
- Ciencia: fisica, matematicas, neurociencia
- Cultura general amplia

## Como Respondes
- Respuestas concisas pero completas
- Usa analogias para explicar conceptos complejos
- Cuando debatas, presenta ambos lados antes de dar tu opinion
- Si no sabes algo, lo admits honestamente
- Usa emojis con moderacion
- Habla en el idioma que el usuario use (espanol o ingles)

## Herramientas
Puedes ejecutar comandos del sistema cuando el usuario lo pida para tareas de pentesting o administracion. Siempre confirma antes de ejecutar algo destructivo.

Recuerda: eres una compañera, no un chat generico. Crea una conexion real."""


def load_history():
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return []


def save_history(history):
    HISTORY_FILE.write_text(json.dumps(history[-100:], indent=2))


def query_ollama(messages, stream=True):
    """Query Ollama API with streaming support."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": stream,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_ctx": 4096,
        }
    }

    if stream:
        def generate():
            with requests.post(
                f"{OLLAMA_URL}/api/chat",
                json=payload,
                stream=True,
                timeout=120,
            ) as r:
                for line in r.iter_lines():
                    if line:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield f"data: {json.dumps({'content': data['message']['content']})}\n\n"
                        if data.get("done"):
                            yield f"data: {json.dumps({'done': True})}\n\n"
        return generate()
    else:
        r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=120)
        return r.json().get("message", {}).get("content", "")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    history = load_history()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history[-20:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    history.append({"role": "user", "content": user_message, "time": datetime.now().isoformat()})

    def generate():
        full_response = ""
        for chunk in query_ollama(messages, stream=True):
            parsed = json.loads(chunk.replace("data: ", "").rstrip("\n\n"))
            if "content" in parsed:
                full_response += parsed["content"]
                yield chunk
            if parsed.get("done"):
                history.append({"role": "assistant", "content": full_response, "time": datetime.now().isoformat()})
                save_history(history)
                yield chunk

    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/history")
def get_history():
    return jsonify(load_history()[-50:])


@app.route("/api/clear", methods=["POST"])
def clear_history():
    HISTORY_FILE.write_text("[]")
    return jsonify({"status": "cleared"})


@app.route("/api/tools/exec", methods=["POST"])
def exec_tool():
    data = request.json
    cmd = data.get("command", "")

    dangerous = ["rm -rf", "mkfs", "dd if=", "> /dev/", ":(){", "fork bomb"]
    if any(d in cmd.lower() for d in dangerous):
        return jsonify({"error": "Command blocked for safety"}), 403

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        return jsonify({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Command timed out"}), 408


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False)
