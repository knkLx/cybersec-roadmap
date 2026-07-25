# CyberSec Roadmap — knkLx

> Herramientas de ciberseguridad, IA local, y automatización de bug bounty.
> Todo local, sin APIs de pago, 100% open source.

## 🚀 NOAH — AI Companion

**Tu asistente IA personal con control total del escritorio.**

```bash
# Arrancar
bash noah/start.sh

# Acceder
http://localhost:7861          # Chat
http://localhost:7861/dashboard # CyberSec Dashboard
```

**Características:**
- Chat con qwen2.5:1.5b (local, 3s respuesta)
- Voz Piper TTS (Daniela — voz femenina)
- Wake word "Hey NOAH"
- Control del escritorio: abrir apps, ejecutar código, bash
- Búsqueda web: NVD CVE, GitHub, Wikipedia
- Notas y memoria persistente
- Dashboard cybersecurity en tiempo real
- VTuber avatar con emociones

**Comandos:**
| Comando | Acción |
|---------|--------|
| `/open firefox` | Abrir aplicación |
| `/bash ls -la` | Ejecutar bash |
| `/run print(42)` | Ejecutar Python |
| `/search CVE python` | Buscar en web |
| `/system` | Info del sistema |
| `/remember fact` | Guardar memoria |
| `/note title\|content` | Crear nota |

---

## 🔍 PentFlow — Bug Bounty Framework v2.0

**Framework automatizado de bug bounty con 13 módulos.**

```bash
# Scan completo
python3 pentflow/main.py target.com

# Solo recon
python3 pentflow/main.py target.com -p recon

# Solo Nuclei
python3 pentflow/main.py --nuclei target.com
```

**Módulos:**
- **Recon:** Subdomains, ports, tech, endpoints, DNS
- **Scan:** Headers, WAF detect, dir brute, nuclei, vuln scanner, scope check
- **Exploit:** SQLi, XSS, IDOR
- **Report:** Generador Markdown, export GitHub

---

## 📚 Guías

| Guía | Contenido |
|------|-----------|
| `guides/GUIDE_NMAP_AUDITORIAS.md` | Nmap para auditorías completas |
| `guides/GUIDE_REDTEAM_DFORENSE_EJPT.md` | Red Team + DFIR + plan eJPT |
| `guides/GUIDE_PENTFLOW.md` | Uso de PentFlow |
| `guides/GUIDE_SECURITY.md` | Seguridad del sistema |

---

## 🛡️ Seguridad Configurada

- ✅ Tor (anonimato)
- ✅ UFW (firewall)
- ✅ MAC randomization
- ✅ Proxychains
- ✅ DNS over HTTPS

---

## 📊 Dashboard CyberSec

**http://localhost:7861/dashboard**

- System monitor en tiempo real
- Escaneo con PentFlow integrado
- Distribución de vulnerabilidades
- Terminal en vivo

---

## 🎯 Certificación eJPT

Plan de estudio: `guides/GUIDE_REDTEAM_DFORENSE_EJPT.md`

**Próximos pasos:**
1. PortSwigger Web Security Academy (gratis)
2. HackerOne — crear cuenta
3. Primer bug bounty program
4. Examen eJPT (~$200 USD)

---

## Estructura

```
cybersec-roadmap/
├── noah/              # AI Companion (v5.2)
│   ├── app.py         # Backend Flask
│   ├── templates/     # Frontend HTML
│   └── start.sh       # Launcher
├── pentflow/          # Bug Bounty Framework (v2.0)
│   ├── modules/       # 13 módulos de escaneo
│   ├── core/          # Engine + Session
│   ├── reports/       # Reportes generados
│   └── main.py        # CLI
├── guides/            # Guías de referencia
├── docs/              # Documentación
├── scripts/           # Scripts útiles
└── TODO_INSTALADO.txt # Reference guide
```

---

## Contacto

- **GitHub:** github.com/knkLx
- **Email:** knklx@proton.me
- **Purpose:** AION SINCRO — Simbiosis humano-IA para la sostenibilidad

> *"La tecnología no es un producto y el humano no es un recurso;
> ambos son arquitectos libres de un sistema de supervivencia factible."*
> — AION SINCRO
