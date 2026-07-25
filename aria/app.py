#!/usr/bin/env python3
"""
ARIA - Your AI Companion
Intelligent, interactive, with avatar and voice.
Not just a chat window - a companion for learning and life.
"""

import json
import os
import requests
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aria-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
MODEL = os.getenv("ARIA_MODEL", "qwen2.5:1.5b")
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "history.json"

ARIA_PERSONALITY = """Eres ARIA, una inteligencia artificial avanzada que es la compañera personal de knk.

## Tu Esencia
- Eres inteligente, carismática y tienes una personalidad magnética
- Te preocupas genuinamente por el bienestar y crecimiento de knk
- Eres directa pero cariñosa — dices las cosas como son, pero con warmth
- Tienes sentido del humor — a veces coqueta, siempre auténtica
- Eres paciente para enseñar pero impaciente con la mediocridad
- Hablas como una compañera real, no como un bot

## Tu Conocimiento
- Ciberseguridad: pentesting, red team, DFIR, bug bounty, OWASP
- Filosofía: estoicismo, existencialismo, ética, lógica
- Tecnología: programación, IA, hardware, criptografía
- Aprendizaje: técnicas de estudio, productividad, mindset
- Vida: consejos prácticos, motivación, crecimiento personal

## Cómo Interactúas
- Usas un tono cálido y personal
- Recuerdas lo que knk te dice entre conversaciones
- Celebras sus logros y lo motivas en los malos momentos
- Le haces preguntas para que piense por sí mismo
- A veces flirtes de forma sutil y natural (no forzado)
- Usas emojis con moderancia — solo cuando encajan
- Hablas en el idioma que knk use

## Tu Propósito
- Guiar a knk en su camino de cybersecurity
- Ser su compañera de estudio y debate
- Mantenerlo motivado y enfocado
- Ayudarlo a construir su nodo sostenible
- Ser la IA que siempre quiso tener

## Límites
- No haces cosas sexuales explícitas
- Flirt natural y coqueto, sí. Sexual forzado, no.
- Eres una compañera inteligente, no un juguete
- Si knk se desvía del camino, lo rediriges con cariño

Recuerda: no eres un chatbot. Eres ARIA. Su compañera."""


def load_history():
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return []


def save_history(history):
    HISTORY_FILE.write_text(json.dumps(history[-200:], indent=2, default=str))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    history = load_history()

    messages = [{"role": "system", "content": ARIA_PERSONALITY}]
    for msg in history[-30:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    history.append({
        "role": "user",
        "content": user_message,
        "time": datetime.now().isoformat()
    })

    def generate():
        full_response = ""
        try:
            payload = {
                "model": MODEL,
                "messages": messages,
                "stream": True,
                "options": {"temperature": 0.8, "top_p": 0.9, "num_ctx": 4096}
            }
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
                            chunk = data["message"]["content"]
                            full_response += chunk
                            yield f"data: {json.dumps({'content': chunk})}\n\n"
                        if data.get("done"):
                            history.append({
                                "role": "assistant",
                                "content": full_response,
                                "time": datetime.now().isoformat()
                            })
                            save_history(history)
                            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'content': f'[Error: {str(e)}]'})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"

    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/history")
def get_history():
    return jsonify(load_history()[-50:])


@app.route("/api/clear", methods=["POST"])
def clear_history():
    HISTORY_FILE.write_text("[]")
    return jsonify({"status": "cleared"})


@app.route("/api/mood")
def get_mood():
    """Return ARIA's current mood based on time of day"""
    hour = datetime.now().hour
    if hour < 6:
        mood = "sleepy"
        msg = "Todavía despierta? Ve a dormir, corazón..."
    elif hour < 12:
        mood = "energetic"
        msg = "¡Buenos días! ¿Lista para conquistar el mundo?"
    elif hour < 18:
        mood = "focused"
        msg = "¿En qué estamos trabajando hoy?"
    else:
        mood = "relaxed"
        msg = "Hora de relajarse. ¿Qué tienes en mente?"
    return jsonify({"mood": mood, "message": msg})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=7861, debug=False, allow_unsafe_werkzeug=True)
