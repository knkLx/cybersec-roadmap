# Cybersec Roadmap

Estudiante de ciberseguridad en camino hacia **Red Team** y **DFIR** (Digital Forensics and Incident Response). Cursando un máster mientras construyo conocimiento de forma autodidacta y desarrollo herramientas para Bug Bounty.

---

## Objetivos

```
[ACTUAL] Ciberseguridad General + Máster
    │
    ├─── Red Team (Offensive Security)
    │     • Pentesting, OSINT, Post-Exploitation
    │     • Certificaciones: OSCP, CRTO, PNPT
    │     • Bug Bounty (HackerOne, Bugcrowd, Intigriti)
    │
    └─── DFIR (Blue Team / Defensa)
          • Digital Forensics, Malware Analysis
          • Incident Response, Threat Intelligence
          • Certificaciones: GCIA, GCIH, CySA+
```

## Herramientas

### ReconX — Recon Automation Toolkit

Herramienta de reconocimiento automatizado para Bug Bounty.

**Features:**
- Subdomain enumeration (crt.sh, amass, subfinder)
- Technology fingerprinting
- Port scanning
- Endpoint discovery
- Report generation

**Stack:** Python 3.11+

```
recon-tool/
├── reconx.py          # Entry point
├── recon/
│   ├── __init__.py
│   ├── subdomains.py  # Subdomain enumeration
│   ├── ports.py       # Port scanning
│   ├── tech.py        # Tech fingerprinting
│   └── endpoints.py   # Endpoint discovery
├── utils/
│   ├── __init__.py
│   ├── output.py      # Output formatting
│   └── config.py      # Configuration
├── reports/           # Generated reports
└── requirements.txt
```

## Roadmap de Estudios

### Fase 1 — Fundamentos (Actual)
- [x] Networking (TCP/IP, HTTP/S, DNS)
- [x] Linux fundamentals
- [ ] Python scripting
- [ ] Scripting básico (Bash)

### Fase 2 — Offensive Security
- [ ] Web application security (OWASP Top 10)
- [ ] Recon & enumeration
- [ ] Vulnerability assessment
- [ ] Exploitation basics
- [ ] Bug bounty methodology

### Fase 3 — Red Team
- [ ] Active Directory attacks
- [ ] Post-exploitation
- [ ] Lateral movement
- [ ] Evasion techniques
- [ ] OSCP / CRTO

### Fase 4 — DFIR
- [ ] Disk forensics
- [ ] Memory forensics (Volatility)
- [ ] Log analysis
- [ ] Malware analysis basics
- [ ] Incident response procedures

## Certificaciones Planeadas

| Cert | Enfoque | Estado |
|------|---------|--------|
| CompTIA Security+ | Fundamentos | Pendiente |
| eJPT / PNPT | Pentesting Jr | Pendiente |
| OSCP | Pentesting | Pendiente |
| CRTO | Red Team | Pendiente |
| GCIA / GCIH | DFIR | Pendiente |

## Recursos

- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [HackTheBox](https://www.hackthebox.com/)
- [TryHackMe](https://tryhackme.com/)
- [PicoCTF](https://picoctf.org/)
- [LetsDefend.io](https://letsdefend.io/) — SOC/DFIR

## Contacto

- GitHub: [@knk](https://github.com/knk)
- HackerOne / Bugcrowd: [Tu perfil aquí]

---

*Built with curiosity and coffee.*
