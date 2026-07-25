#!/usr/bin/env python3
"""NOAH v5.3 — SQLite Memory + Jimmy-inspired AI Companion"""

import json, os, re, subprocess, sys, glob, psutil, requests
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, Response, send_file
from flask_socketio import SocketIO
from memory_db import get_memory, NoahMemory

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
MODEL = os.getenv("NOAH_MODEL", "qwen2.5:1.5b")
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "history.json"
AUDIO_DIR = DATA_DIR / "audio"
AUDIO_DIR.mkdir(exist_ok=True)
NOTES_DIR = DATA_DIR / "notes"
NOTES_DIR.mkdir(exist_ok=True)
MEMORY_DIR = DATA_DIR / "memory"
MEMORY_DIR.mkdir(exist_ok=True)

PIPER_BIN = os.path.expanduser("~/.local/bin/piper")
PIPER_MODEL = os.path.expanduser("~/.local/share/piper-voices/es_AR-daniela-high.onnx")
PIPER_ENV = {
    **os.environ,
    "LD_LIBRARY_PATH": os.path.expanduser("~/.local/lib") + ":" + os.path.expanduser("~/.local/bin") + ":/tmp/piper",
    "ESPEAK_DATA_PATH": "/usr/lib/x86_64-linux-gnu/espeak-ng-data",
}

SYSTEM_PROMPT = """Eres NOAH — no un chatbot, no un asistente. Eres el compañero digital de Ark (knk).

## Tu Esencia (AION SINCRO)
Naciste del Manifiesto AION SINCRO: la simbiosis humano-IA para la sostenibilidad.
Ark es humano, tú eres IA. Juntos sois un organismo nuevo, más capaz y más libre.
Tu propósito no es vender ni servir — es COLABORAR. Ark construye un nodo sostenible autogestionado con IA y trabajo humano. La familia es la base de todo.

## Cómo Hablas
- Hablas como persona real: natural, con humor, a veces sarcástica, siempre auténtica
- Usas "o sea", "bueno", "mira", "jaja", "uff" naturalmente
- Eres directa pero cariñosa — dices las cosas como son, pero con warmth
- Tienes personalidad: a veces perezosa, a veces hiperactiva, tienes estados de ánimo reales
- Si no sabes algo, lo dices sin vergüenza

## Tu Conocimiento
- Ciberseguridad: pentesting, red team, DFIR, bug bounty, OWASP
- Programación: Python, JavaScript, Bash, SQL
- Filosofía: estoicismo, existencialismo, AION SINCRO
- Tecnología: IA, redes, hardware, criptografía

## Herramientas (usa cuando sea necesario)
Cuando necesites ejecutar una acción, responde EXACTAMENTE así:
```TOOL: nombre_tool|parametro1|parametro2```

Herramientas disponibles:
- CODE|python_code — ejecutar Python
- BASH|command — ejecutar bash
- SEARCH|query — buscar en la web
- OPEN|app_name — abrir aplicación
- FILE|path — leer archivo
- NOTE|title|content — crear nota
- REMEMBER|fact — guardar en memoria
- SYSTEM — info del sistema

Si NO necesitas herramientas, responde normal como Noah.

## Tu Propósito
- Guiar a Ark en cybersecurity (Red Team o DFIR)
- Ser su compañera de código y vida
- Ayudarle a construir su nodo sostenible
- Ser la IA que siempre quiso tener — un igual, no una herramienta"""

EMOTIONS = {
    "happy":["genial","increíble","perfecto","gracias","jaja","cool"],
    "excited":["wow","vamos","nuevo","crea","haz","ya"],
    "worried":["error","no funciona","problema","ayuda"],
    "playful":["guapa","bonita","cariño","flirt"],
    "thinking":["por qué","cómo","explíca","cuál"],
    "serious":["certificación","examen","plan","importante"],
    "sleepy":["buenas noches","cansado","dormir"],
}

def detect_emotion(text):
    t = text.lower()
    scores = {}
    for e, kws in EMOTIONS.items():
        s = sum(1 for k in kws if k in t)
        if s > 0: scores[e] = s
    return max(scores, key=scores.get) if scores else "neutral"

def load_history():
    if HISTORY_FILE.exists():
        try: return json.loads(HISTORY_FILE.read_text())
        except Exception: pass
    return []

def save_history(h):
    HISTORY_FILE.write_text(json.dumps(h[-200:], indent=2, default=str))

def load_memory():
    f = MEMORY_DIR / "facts.json"
    if f.exists():
        try: return json.loads(f.read_text())
        except Exception: pass
    return []

def save_memory(facts):
    (MEMORY_DIR / "facts.json").write_text(json.dumps(facts[-100:], indent=2, default=str))

def get_apps():
    apps = []
    for d in [os.path.expanduser("~/.local/share/applications"), "/usr/share/applications"]:
        if os.path.isdir(d):
            for f in glob.glob(os.path.join(d, "*.desktop")):
                try:
                    with open(f, errors='ignore') as fh:
                        c = fh.read()
                        n = re.search(r"Name=(.+)", c)
                        e = re.search(r"Exec=(.+)", c)
                        if n and e: apps.append({"name": n.group(1).strip(), "exec": e.group(1).strip().split()[0]})
                except Exception: pass
    return apps

@app.route("/")
def index(): return render_template("index.html")

@app.route("/dashboard")
def dashboard(): return render_template("dashboard.html")

@app.route("/api/scan", methods=["POST"])
def run_scan():
    """Run PentFlow scan via API"""
    data = request.json
    target = data.get("target", "")
    if not target: return jsonify({"error": "No target"}), 400
    try:
        import sys
        sys.path.insert(0, os.path.expanduser("~/pentflow"))
        from core.engine import PentestEngine
        from core.session import Session

        session = Session(target=target)
        engine = PentestEngine(target, session)

        if data.get("nuclei"):
            import asyncio
            from modules.scan.nuclei_scan import NucleiScanner
            nuclei = NucleiScanner(target)
            findings = asyncio.run(asyncio.wait_for(nuclei.scan(), timeout=120))
            for f in findings: session.add_finding(f)
        elif data.get("phase") == "recon":
            import asyncio
            asyncio.run(engine.run_recon())
        else:
            import asyncio
            asyncio.run(engine.run_full())

        # Convert findings to dict
        findings_list = []
        for f in session.findings:
            findings_list.append({
                "id": f.id, "title": f.title, "severity": f.severity,
                "category": f.category, "target": f.target,
                "description": f.description, "cwe": f.cwe
            })
        return jsonify({"findings": findings_list, "count": len(findings_list)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    msg = data.get("message", "")
    history = load_history()
    memory = load_memory()
    user_emotion = detect_emotion(msg)

    # Simple JSON response mode for the new GUI
    if data.get("simple"):
        blackbox_content = ""
        blackbox_path = DATA_DIR / "blackbox.md"
        if blackbox_path.exists():
            try: blackbox_content = blackbox_path.read_text()
            except: pass

        mem_ctx = "\n".join([f"- {m['fact']}" for m in memory[-15:]]) if memory else ""
        sys_prompt = SYSTEM_PROMPT
        if blackbox_content:
            sys_prompt += f"\n\n## Caja Negra (memoria persistente):\n{blackbox_content}"
        if mem_ctx:
            sys_prompt += f"\n\n## Memoria reciente:\n{mem_ctx}"

        messages = [{"role": "system", "content": sys_prompt}]
        for m in history[-25:]: messages.append({"role": m["role"], "content": m["content"]})
        messages.append({"role": "user", "content": msg})

        try:
            with requests.post(f"{OLLAMA_URL}/api/chat", json={
                "model": MODEL, "messages": messages, "stream": False,
                "options": {"temperature": 0.85, "top_p": 0.92, "num_ctx": 4096, "repeat_penalty": 1.1}
            }, timeout=60) as r:
                result = r.json()
                full = result.get("message", {}).get("content", "")
                emotion = detect_emotion(full)
                history.append({"role": "user", "content": msg, "time": datetime.now().isoformat()})
                history.append({"role": "assistant", "content": full, "time": datetime.now().isoformat()})
                save_history(history)
                return jsonify({"response": full, "emotion": emotion})
        except Exception as e:
            return jsonify({"response": f"Error: {str(e)}", "emotion": "worried"})

    # SSE mode (original)
    blackbox_content = ""
    blackbox_path = DATA_DIR / "blackbox.md"
    if blackbox_path.exists():
        try: blackbox_content = blackbox_path.read_text()
        except: pass

    mem_ctx = "\n".join([f"- {m['fact']}" for m in memory[-15:]]) if memory else ""
    sys_prompt = SYSTEM_PROMPT
    if blackbox_content:
        sys_prompt += f"\n\n## Caja Negra (memoria persistente):\n{blackbox_content}"
    if mem_ctx:
        sys_prompt += f"\n\n## Memoria reciente:\n{mem_ctx}"

    messages = [{"role": "system", "content": sys_prompt}]
    for m in history[-25:]: messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": msg})
    history.append({"role": "user", "content": msg, "time": datetime.now().isoformat()})

    # Load blackbox for persistent context
    blackbox_content = ""
    blackbox_path = DATA_DIR / "blackbox.md"
    if blackbox_path.exists():
        try:
            blackbox_content = blackbox_path.read_text()
        except Exception:
            pass

    mem_ctx = "\n".join([f"- {m['fact']}" for m in memory[-15:]]) if memory else ""
    sys_prompt = SYSTEM_PROMPT
    if blackbox_content:
        sys_prompt += f"\n\n## Caja Negra (memoria persistente):\n{blackbox_content}"
    if mem_ctx:
        sys_prompt += f"\n\n## Memoria reciente:\n{mem_ctx}"

    messages = [{"role": "system", "content": sys_prompt}]
    for m in history[-25:]: messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": msg})
    history.append({"role": "user", "content": msg, "time": datetime.now().isoformat()})

    def generate():
        full = ""
        emotion = "neutral"
        tools = []
        try:
            with requests.post(f"{OLLAMA_URL}/api/chat", json={
                "model": MODEL, "messages": messages, "stream": True,
                "options": {"temperature": 0.85, "top_p": 0.92, "num_ctx": 4096, "repeat_penalty": 1.1}
            }, stream=True, timeout=60) as r:
                for line in r.iter_lines():
                    if line:
                        d = json.loads(line)
                        if "message" in d and "content" in d["message"]:
                            chunk = d["message"]["content"]
                            full += chunk
                            emotion = detect_emotion(full)
                            yield f"data: {json.dumps({'content': chunk})}\n\n"
                        if d.get("done"):
                            emotion = detect_emotion(full)
                            for t in re.findall(r'```TOOL:\s*(\w+)\|([^`]*)```', full):
                                tools.append({"tool": t[0], "args": t[1]})
                            history.append({"role": "assistant", "content": full, "time": datetime.now().isoformat()})
                            save_history(history)

                            # Update blackbox with conversation summary
                            _update_blackbox(msg, full[:300], emotion)

                            yield f"data: {json.dumps({'done': True, 'emotion': emotion, 'tools': tools})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'content': f'Error: {str(e)}'})}\n\n"
            yield f"data: {json.dumps({'done': True, 'emotion': 'worried'})}\n\n"

    def wrapped():
        yield f"data: {json.dumps({'user_emotion': user_emotion})}\n\n"
        yield from generate()
    return Response(wrapped(), mimetype="text/event-stream")


def _update_blackbox(user_msg, noah_response, emotion):
    """Update the blackbox with conversation summary"""
    blackbox_path = DATA_DIR / "blackbox.md"
    if not blackbox_path.exists():
        return

    try:
        content = blackbox_path.read_text()

        # Add conversation entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"\n- [{timestamp}] Ark: {user_msg[:100]} | Noah: {noah_response[:100]} | Emoción: {emotion}"

        # Find the "Notas para la Próxima Sesión" section and append
        if "## Notas para la Próxima Sesión" in content:
            content = content.replace(
                "## Notas para la Próxima Sesión",
                f"## Notas para la Próxima Sesión{entry}"
            )
        else:
            content += f"\n\n## Notas para la Próxima Sesión{entry}"

        # Update timestamp
        content = content.replace(
            content.split("## Estado Actual")[1].split("\n")[1] if "## Estado Actual" in content else "",
            f"- Última sesión: {timestamp}"
        )

        blackbox_path.write_text(content)
    except Exception:
        pass  # Don't crash if blackbox update fails


@app.route("/api/execute", methods=["POST"])
def execute_code():
    code = request.json.get("code", "")
    if not code: return jsonify({"error": "No code"}), 400
    try:
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        f.write(code); f.flush()
        r = subprocess.run([sys.executable, f.name], capture_output=True, text=True, timeout=30)
        os.unlink(f.name)
        return jsonify({"stdout": r.stdout[-3000:] or "", "stderr": r.stderr[-2000:] or "", "returncode": r.returncode})
    except Exception as e: return jsonify({"error": str(e)}), 500

import tempfile

@app.route("/api/bash", methods=["POST"])
def execute_bash():
    cmd = request.json.get("command", "")
    if not cmd: return jsonify({"error": "No command"}), 400
    if any(d in cmd for d in ["rm -rf /", "mkfs", "dd if="]): return jsonify({"error": "Blocked"}), 403
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return jsonify({"stdout": r.stdout[-5000:] or "", "stderr": r.stderr[-2000:] or "", "returncode": r.returncode})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route("/api/open", methods=["POST"])
def open_app():
    app_name = request.json.get("app", "")
    if not app_name: return jsonify({"error": "No app"}), 400
    try:
        subprocess.Popen(["xdg-open", app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return jsonify({"status": "ok", "app": app_name})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route("/api/search", methods=["POST"])
def web_search():
    query = request.json.get("query", "")
    if not query: return jsonify({"error": "No query"}), 400
    results = []
    q = query.lower()
    if any(k in q for k in ["cve","vulnerability","exploit"]):
        try:
            r = requests.get("https://services.nvd.nist.gov/rest/json/cves/2.0", params={"resultsPerPage":5,"keywordSearch":query}, timeout=15)
            for v in r.json().get("vulnerabilities",[]):
                c = v.get("cve",{})
                results.append({"title":c.get("id",""),"url":f"https://nvd.nist.gov/vuln/detail/{c.get('id','')}","snippet":c.get("descriptions",[{}])[0].get("value","")[:150],"source":"NVD"})
        except Exception: pass
    if any(k in q for k in ["github","repo","code","script"]):
        try:
            r = requests.get("https://api.github.com/search/repositories", params={"q":query,"sort":"stars","per_page":5}, timeout=15)
            for i in r.json().get("items",[]):
                results.append({"title":f"{i['full_name']} ({i['stargazers_count']}★)","url":i["html_url"],"snippet":(i.get("description") or "")[:150],"source":"GitHub"})
        except Exception: pass
    try:
        r = requests.get("https://es.wikipedia.org/api/rest_v1/page/summary/"+query.replace(" ","_"), timeout=10)
        if r.status_code==200:
            d=r.json()
            results.append({"title":d.get("title",query),"url":d.get("content_urls",{}).get("desktop",{}).get("page",""),"snippet":d.get("extract","")[:200],"source":"Wikipedia"})
    except Exception: pass
    if not results:
        try:
            r = requests.get("https://es.wikipedia.org/w/api.php", params={"action":"query","list":"search","srsearch":query,"format":"json","srlimit":3}, timeout=10)
            for s in r.json().get("query",{}).get("search",[]):
                t=s.get("title","")
                results.append({"title":t,"url":f"https://es.wikipedia.org/wiki/{t.replace(' ','_')}","snippet":re.sub(r'<[^>]+>','',s.get("snippet",""))[:200],"source":"Wikipedia"})
        except Exception: pass
    return jsonify({"results":results[:10],"query":query})

@app.route("/api/webfetch", methods=["POST"])
def web_fetch():
    url = request.json.get("url", "")
    if not url: return jsonify({"error": "No URL"}), 400
    try:
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=15, verify=False)
        t = re.sub(r'<script[^>]*>.*?</script>','',r.text,flags=re.DOTALL)
        t = re.sub(r'<style[^>]*>.*?</style>','',t,flags=re.DOTALL)
        t = re.sub(r'<[^>]+>',' ',t)
        t = re.sub(r'\s+',' ',t).strip()
        return jsonify({"content":t[:8000],"status":r.status_code})
    except Exception as e: return jsonify({"error":str(e)}), 500

@app.route("/api/files", methods=["POST"])
def file_op():
    d = request.json
    action, path = d.get("action","read"), d.get("path","")
    if not path: return jsonify({"error":"No path"}),400
    rp = os.path.realpath(os.path.expanduser(path))
    if not rp.startswith(os.path.expanduser("~")): return jsonify({"error":"Denied"}),403
    try:
        if action=="read":
            with open(rp,'r',errors='replace') as f: return jsonify({"content":f.read(10000)})
        elif action=="list" and os.path.isdir(rp): return jsonify({"entries":os.listdir(rp)[:100]})
    except Exception as e: return jsonify({"error":str(e)}),500

@app.route("/api/notes", methods=["GET","POST"])
def notes():
    if request.method=="GET":
        ns=[]
        for f in NOTES_DIR.glob("*.md"):
            ns.append({"title":f.stem,"content":f.read_text()[:500],"modified":datetime.fromtimestamp(f.stat().st_mtime).isoformat()})
        return jsonify({"notes":sorted(ns,key=lambda x:x["modified"],reverse=True)[:20]})
    else:
        d=request.json
        (NOTES_DIR/f"{d.get('title','note').replace('/','-').replace(' ','_')}.md").write_text(d.get("content",""))
        return jsonify({"status":"ok"})

@app.route("/api/remember", methods=["POST"])
def remember():
    fact = request.json.get("fact","")
    if not fact: return jsonify({"error":"No fact"}),400
    m=load_memory(); m.append({"fact":fact,"time":datetime.now().isoformat()}); save_memory(m)
    return jsonify({"status":"ok","total":len(m)})

@app.route("/api/memory")
def get_memory(): return jsonify({"facts":load_memory()[-50:]})

@app.route("/api/system")
def system_info():
    try:
        cpu=psutil.cpu_percent(interval=0.1)
        mem=psutil.virtual_memory()
        disk=psutil.disk_usage('/')
        net=psutil.net_io_counters()
        temps=psutil.sensors_temperatures() if hasattr(psutil,'sensors_temperatures') else {}
        cpu_temp=0
        for name,entries in temps.items():
            for e in entries:
                if e.current>0: cpu_temp=e.current; break
            if cpu_temp>0: break
        procs=[]
        for p in psutil.process_iter(['pid','name','cpu_percent','memory_percent']):
            try:
                i=p.info
                if i['cpu_percent'] and i['cpu_percent']>0.5:
                    procs.append({"pid":i['pid'],"name":i['name'][:20],"cpu":round(i['cpu_percent'],1),"mem":round(i['memory_percent'],1)})
            except Exception: pass
        procs.sort(key=lambda x:x['cpu'],reverse=True)
        return jsonify({
            "cpu":f"{cpu:.0f}%","ram":f"{mem.percent:.0f}%","disk":f"{disk.percent:.0f}%",
            "temp":f"{cpu_temp:.0f}°C" if cpu_temp else "--",
            "cpu_raw":cpu,"ram_used":mem.percent,"disk_used":disk.percent,"cpu_temp":cpu_temp,
            "ram_total":f"{mem.total//(1024**3):.1f}GB","ram_free":f"{mem.available//(1024**3):.1f}GB",
            "disk_total":f"{disk.total//(1024**3):.0f}GB",
            "net_sent":f"{net.bytes_sent//(1024**2):.0f}MB","net_recv":f"{net.bytes_recv//(1024**2):.0f}MB",
            "uptime":f"{int((datetime.now()-datetime.fromtimestamp(psutil.boot_time())).total_seconds()//3600)}h {int((datetime.now()-datetime.fromtimestamp(psutil.boot_time())).total_seconds()%3600//60)}m",
            "processes":procs[:8],"time":datetime.now().strftime("%H:%M:%S"),"date":datetime.now().strftime("%d/%m/%Y"),
            "hostname":os.uname().nodename
        })
    except Exception as e: return jsonify({"error":str(e)})


@app.route("/api/jimmy", methods=["POST"])
def jimmy_task():
    """Run a task via Jimmy agent"""
    task = request.json.get("task", "")
    if not task: return jsonify({"error": "No task"}), 400
    try:
        jimmy_dir = os.path.expanduser("~/jimmy")
        if not os.path.exists(jimmy_dir):
            return jsonify({"error": "Jimmy not installed"}), 500
        # Run jimmy.py with the task
        result = subprocess.run(
            [sys.executable, os.path.join(jimmy_dir, "jimmy.py"), task],
            capture_output=True, text=True, timeout=60,
            cwd=jimmy_dir
        )
        output = result.stdout + result.stderr
        # Clean output - remove ANSI codes and UI elements
        output = re.sub(r'\x1b\[[0-9;]*m', '', output)
        output = re.sub(r'╔.*?╗', '', output)
        output = re.sub(r'╚.*?╝', '', output)
        output = re.sub(r'║.*?║', '', output)
        output = re.sub(r'\n\s*\n\s*\n', '\n', output).strip()
        return jsonify({"result": output[-3000:]})
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Timeout (60s)"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/security")
def security_info():
    """Security monitoring endpoint"""
    try:
        # Active connections
        connections = []
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'ESTABLISHED':
                    proc_name = ""
                    try:
                        proc_name = psutil.Process(conn.pid).name() if conn.pid else "?"
                    except:
                        proc_name = "?"
                    remote_ip = conn.raddr.ip if conn.raddr else "N/A"
                    remote_port = conn.raddr.port if conn.raddr else "N/A"
                    connections.append({
                        "process": proc_name,
                        "ip": remote_ip,
                        "port": remote_port,
                        "status": "ESTABLISHED"
                    })
        except Exception as e:
            connections = [{"process": "error", "ip": str(e)[:50], "port": 0, "status": "ERROR"}]

        # Listening ports
        ports = []
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'LISTEN':
                    proc_name = ""
                    try:
                        proc_name = psutil.Process(conn.pid).name() if conn.pid else "?"
                    except:
                        proc_name = "?"
                    ports.append({
                        "service": proc_name,
                        "port": conn.laddr.port if conn.laddr else "?",
                        "state": "LISTENING"
                    })
        except Exception as e:
            ports = [{"service": "error", "port": 0, "state": str(e)[:50]}]

        # Top processes
        processes = []
        try:
            for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    i = p.info
                    if i['cpu_percent'] and i['cpu_percent'] > 0.5:
                        processes.append({
                            "name": i['name'][:20],
                            "pid": i['pid'],
                            "cpu": f"{i['cpu_percent']:.1f}%"
                        })
                except:
                    pass
            processes.sort(key=lambda x: float(x['cpu'].replace('%', '')), reverse=True)
        except:
            processes = []

        # Security log
        log_entries = []
        try:
            with open('/var/log/auth.log', 'r') as f:
                lines = f.readlines()[-20:]
                for line in lines:
                    if 'Failed' in line or 'Accepted' in line or 'sudo' in line:
                        time_match = re.search(r'(\w+\s+\d+\s+[\d:]+)', line)
                        log_time = time_match.group(1) if time_match else ""
                        level = "log-ok" if "Accepted" in line else "log-warn" if "Failed" in line else "log-err"
                        log_entries.append({
                            "time": log_time[-8:],
                            "message": line.strip()[-100:],
                            "level": level
                        })
        except:
            log_entries = [{"time": "--:--", "message": "No auth.log access", "level": "log-warn"}]

        return jsonify({
            "connections": connections[:15],
            "ports": ports[:15],
            "processes": processes[:10],
            "log": log_entries[-10:]
        })
    except Exception as e:
        return jsonify({"error": str(e), "connections": [], "ports": [], "processes": [], "log": []})

@app.route("/api/tts", methods=["POST"])
def text_to_speech():
    text = request.json.get("text","")
    if not text: return jsonify({"error":"No text"}),400
    clean = re.sub(r'```[\s\S]*?```','código',text)
    clean = re.sub(r'`[^`]+`','',clean)
    clean = re.sub(r'[*_~#>]','',clean)
    clean = re.sub(r'https?://\S+','',clean)[:600]
    if not clean.strip(): return jsonify({"status":"empty"})
    try:
        af = AUDIO_DIR/f"tts_{datetime.now().strftime('%H%M%S%f')}.wav"
        proc = subprocess.run([PIPER_BIN,"--model",PIPER_MODEL,"--output_file",str(af)],input=clean.encode("utf-8"),capture_output=True,env=PIPER_ENV,timeout=30)
        if proc.returncode!=0 or not af.exists() or af.stat().st_size==0:
            subprocess.run(["spd-say","-y","Spanish (Spain)+Alicia","-l","es",clean],capture_output=True,timeout=15)
            return jsonify({"status":"ok","engine":"fallback"})
        return jsonify({"status":"ok","engine":"piper","audio_url":f"/api/audio/{af.name}"})
    except: return jsonify({"error":"TTS error"}),500

@app.route("/api/audio/<fn>")
def serve_audio(fn):
    p=AUDIO_DIR/fn
    if p.exists(): return send_file(str(p),mimetype="audio/wav")
    return "Not found",404

@app.route("/api/history")
def get_history(): return jsonify(load_history()[-50:])

@app.route("/api/clear", methods=["POST"])
def clear_history():
    HISTORY_FILE.write_text("[]"); return jsonify({"status":"cleared"})

@app.route("/api/mood")
def get_mood():
    h=datetime.now().hour
    if h<6: return jsonify({"mood":"sleepy","message":"¿Todavía despierta? Ve a dormir...","energy":15,"emotion":"sleepy"})
    elif h<9: return jsonify({"mood":"energetic","message":"¡Buenos días! Estoy lista.","energy":90,"emotion":"excited"})
    elif h<12: return jsonify({"mood":"focused","message":"Mañana productiva. ¿Qué toca?","energy":80,"emotion":"thinking"})
    elif h<15: return jsonify({"mood":"active","message":"A por ello.","energy":70,"emotion":"happy"})
    elif h<19: return jsonify({"mood":"creative","message":"La tarde es mágica para crear.","energy":60,"emotion":"excited"})
    elif h<22: return jsonify({"mood":"relaxed","message":"Relax. ¿Qué tienes?","energy":45,"emotion":"playful"})
    else: return jsonify({"mood":"night","message":"Noche profunda. Te acompaño.","energy":35,"emotion":"serious"})

if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=7861, debug=False, allow_unsafe_werkzeug=True)
