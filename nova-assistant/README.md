# NOVA - Personal AI Assistant

Tu Jarvis personal. Asistente de IA local, open source, con interfaz cyberpunk holográfica.

## Características

- **100% Local** — Modelo Qwen2.5 corriendo via Ollama, sin internet ni APIs externas
- **Interfaz tipo Jarvis** — UI holográfica cyberpunk con animaciones en tiempo real
- **Personalidad** — No es un chat genérico, tiene opiniones, humor y contexto
- **Especializado en**:
  - Pentesting y ciberseguridad
  - Filosofía y debate intelectual
  - Programación y tecnología
  - Cultura general
- **Herramientas** — Puede ejecutar comandos del sistema para tareas de pentesting
- **Historial** — Conversaciones persistidas en JSON

## Arquitectura

```
┌─────────────────────────────────┐
│         NOVA Frontend           │
│    (HTML/CSS/JS - Jarvis UI)    │
└──────────────┬──────────────────┘
               │ HTTP
┌──────────────▼──────────────────┐
│      Flask Backend (Python)     │
│   - Chat API (SSE streaming)    │
│   - System prompt engine        │
│   - Tool execution layer        │
│   - History persistence         │
└──────────────┬──────────────────┘
               │ API
┌──────────────▼──────────────────┐
│       Ollama (Local LLM)        │
│    - qwen2.5:1.5b (CPU/GPU)    │
│    - Sin dependencia externa    │
└─────────────────────────────────┘
```

## Requisitos

- Python 3.10+
- Ollama (instalado)
- 2GB+ RAM libre

## Instalación

```bash
# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:1.5b

# Instalar dependencias
pip install flask requests

# Ejecutar
cd nova-assistant
python app.py
```

Abrir **http://localhost:7860** en el navegador.

## Modos

| Modo | Descripción |
|------|-------------|
| PENTEST | Enfocado en seguridad ofensiva y vulnerabilidades |
| PHILOSOPHY | Debate filosófico, ética, lógica |
| CODE | Programación, algoritmos, arquitectura |
| GENERAL | Sin restricciones |

## Para el futuro: Holograma

Esta interfaz web es la base perfecta para integración con:
- **Razer Ava** — Display holográfico interactivo
- **Proyecciones holográficas** — WebRTC + display transparente
- **Realidad aumentada** — WebXR para AR/VR

La UI está diseñada para ser compatible con cualquier display holográfico.

## License

MIT
