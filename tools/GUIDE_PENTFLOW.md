# PentFlow — Guía Completa de Uso

## Qué es PentFlow
Framework automatizado de bug bounty. Escanea targets, encuentra vulnerabilidades, genera reportes profesionales y los sube a GitHub.

## Ubicación
```
~/pentflow/
```

## Instalación
```bash
cd ~/pentflow
pip install -r requirements.txt
```

## Comandos Básicos

### Scan completo (recommended)
```bash
python3 main.py https://target.com
```
Esto ejecuta: Recon → Scan → Exploit → Report

### Fases individuales
```bash
# Solo recon (subdomains, DNS, ports, tech, endpoints)
python3 main.py https://target.com -p recon

# Solo vulnerability scanning
python3 main.py https://target.com -p scan

# Solo exploitation (XSS, SQLi)
python3 main.py https://target.com -p exploit

# Solo generar reporte
python3 main.py https://target.com -p report
```

### Con Nuclei
```bash
# Nuclei con todos los templates
python3 main.py https://target.com --nuclei

# Solo XSS y SQLi
python3 main.py https://target.com --nuclei --nuclei-tags xss,sqli

# Solo CVEs
python3 main.py https://target.com --nuclei --nuclei-tags cve

# Solo critical y high
python3 main.py https://target.com --nuclei --nuclei-severity high,critical

# Template específico
python3 main.py https://target.com --nuclei --nuclei-template ~/nuclei-templates/http/cves/
```

### Gestión de sesiones
```bash
# Ver todas las sesiones
python3 main.py --list

# Reanudar una sesión
python3 main.py https://target.com -s target.com_20260725_XXXXXX
```

### Exportar a GitHub
```bash
python3 main.py --export <session_id>
```

### A través de Tor
```bash
~/pentflow/pentflow-tor https://target.com
```

## Flujo de Trabajo para Bug Bounty

### Paso 1: Elegir programa
Ve a hackerone.com/programs o bugcrowd.com/programs
Busca programas con "bounty" y "safe harbor"

### Paso 2: Leer el scope
ANTES de escanear, lee:
- In-serve: qué dominios puedes tocar
- Out-of-scope: qué NO puedes tocar
- Reglas: rate limits, horarios, prohibiciones

### Paso 3: Recon
```bash
python3 main.py target.com -p recon
```
Guarda los subdomains que encuentre. Ahí están los jewels.

### Paso 4: Scan contra cada subdomain
```bash
python3 main.py admin.target.com -p scan
python3 main.py api.target.com -p scan
python3 main.py staging.target.com -p scan
python3 main.py dev.target.com -p scan
```

### Paso 5: Nuclei contra los interesantes
```bash
python3 main.py staging.target.com --nuclei --nuclei-severity high,critical
```

### Paso 6: Generar reporte
```bash
python3 main.py target.com -p report
```
El reporte se guarda en ~/pentflow/reports/

### Paso 7: Reportar
Copia el hallazgo y súbelo al programa en HackerOne/Bugcrowd

## Qué Buscar (Checklist)

- [ ] .git/config expuesto → Clonar repo, buscar secrets
- [ ] .env expuesto → API keys, DB creds
- [ ] staging/dev/test subdomains accesibles
- [ ] CORS mal configurado → Origin reflection
- [ ] Open redirect → Chain con phishing
- [ ] XSS en parámetros
- [ ] SQLi en parámetros
- [ ] IDOR en APIs
- [ ] Default credentials
- [ ] Backup files (.zip, .sql, .bak)

## Reportes

Los reportes se guardan en:
```
~/pentflow/reports/
├── report_target.com_20260725_035045.md    (Markdown)
├── report_target.com_20260725_035045.html  (HTML con tema oscuro)
```

Cada reporte incluye:
- Executive Summary con severidades
- Cada finding con ID, CWE, evidencia, remediación
- Resultados de recon (subdomains, ports, tech)
- Disclaimer legal

## Solución de Problemas

**Error: "No module named flask"**
```bash
pip install flask requests
```

**Nuclei no encuentra nada**
```bash
nuclei -ut  # Actualizar templates
```

**Reporte no se genera (URL con https://)**
Ya corregido en v1.0.1

**Timeout en scans grandes**
Aumenta el timeout:
```bash
timeout 300 python3 main.py target.com
```

## Cómo Aporta a la Comunidad

1. **Reporta vulnerabilidades** → Los vendors arreglan sus sistemas
2. **Comparte write-ups** → Otros aprenden de tus hallazgos
3. **Contribuye a PentFlow** → Agrega nuevos módulos
4. **Enseña** → Tu experiencia ayuda a otros pentesters
