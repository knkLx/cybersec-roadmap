# NOVA — Guía Completa de Uso

## Qué es NOVA
Asistente de IA personal tipo Jarvis. Modelo local (sin internet), interfaz cyberpunk, voz, pentesting + filosofía.

## Ubicación
```
~/nova-assistant/
```

## Requisitos
- Ollama instalado (`~/.local/bin/ollama`)
- Modelo qwen2.5:1.5b descargado
- Flask instalado

## Iniciar NOVA

### Método 1: Script automático (recommended)
```bash
cd ~/nova-assistant
./start.sh
```

### Método 2: Manual
```bash
# Terminal 1: Ollama
export PATH="$HOME/.local/bin:$PATH"
ollama serve &

# Terminal 2: NOVA
cd ~/nova-assistant
python3 app.py
```

### Abrir en navegador
```
http://localhost:7860
http://192.168.1.17:7860  (desde otra máquina)
```

## Funciones

### Chat de texto
Escribe en el input y presiona Enter

### Voz (speech-to-text)
1. Haz click en el botón del micrófono (izquierda del input)
2. Habla
3. NOVA escucha y escribe automáticamente
4. Responde y si el mic está activo, lee la respuesta

### Modos
| Modo | Para qué |
|------|----------|
| PENTEST | Preguntas sobre seguridad, vulnerabilidades, tools |
| PHILOSOPHY | Debate filosófico, ética, lógica |
| CODE | Programación, algoritmos, debugging |
| GENERAL | Sin restricciones |

### Quick Actions
- XSS — Explica XSS
- Filosofia — Habla de estoicismo
- Ideas — Brainstorming
- Roadmap — Qué aprender para pentesting

## Preguntas Útiles para NOVA

### Pentesting
- "Explica cómo funciona un ataque XSS"
- "Cuáles son las 10 vulnerabilidades más comunes en APIs"
- "Cómo hago fuzzing de un endpoint"
- "Explícame IDOR con ejemplos"
- "Qué certs debo sacar para Red Team"

### Filosofía
- "Debate: el determinismo vs el libre albedrío"
- "Qué decía Sócrates sobre el conocimiento"
- "Es ético hackear para un bien mayor"
- "Explica la navaja de Ockham"

### Code
- "Escribe un script de Python para escanear puertos"
- "Cómo automatizo reportes con Jinja2"
- "Explica este código: [pega código]"

## Personalidad de NOVA

NOVA no es un chat genérico. Tiene:
- Opiniones propias
- Sentido del humor (un poco sarcástico)
- Prefiere debate a respuestas monosílabas
- Es directa pero amigable
- Puede discutir contigo

## Seguridad

- Todo corre LOCALMENTE — sin APIs externas
- Sin envío de datos a la nube
- Modelo 100% offline
- Historial guardado en JSON local

## Para el Futuro: Holograma

La interfaz web es compatible con:
- Razer Ava (display holográfico)
- WebXR para AR/VR
- Proyecciones holográficas web
- Solo necesitas el hardware

## Solución de Problemas

**"No module named flask"**
```bash
pip install flask requests
```

**Ollama no arranca**
```bash
export PATH="$HOME/.local/bin:$PATH"
ollama serve &
```

**Modelo no responde**
```bash
ollama pull qwen2.5:1.5b
```

**No hay audio**
Usa Chrome (mejor soporte de Web Speech API)

**Input no funciona**
Recarga la página (Ctrl+Shift+R)
