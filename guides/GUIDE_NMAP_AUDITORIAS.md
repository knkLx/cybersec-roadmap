# Guía Nmap para Auditorías de Seguridad
# De principiante a auditor en 7 días

---

## INSTALACIÓN

```bash
# Kali/Parrot (ya viene instalado)
nmap --version

# Ubuntu/Debian
sudo apt install nmap -y

# Con NSE scripts
ls /usr/share/nmap/scripts/ | wc -l  # Debería ser 200+
```

---

## FASE 1: RECONOCIMIENTO PASIVO (sin tocar el target)

```bash
# DNS básico
nslookup target.com
dig target.com ANY
dig target.com AXFR  # Zone transfer

# Subdomain enumeration
subfinder -d target.com -o subdomains.txt
amass enum -passive -d target.com -o subdomains.txt
assetfinder --subs-only target.com >> subdomains.txt

# Certificados SSL
echo | openssl s_client -connect target.com:443 2>/dev/null | openssl x509 -noout -dates
crt.sh/?q=%.target.com  # Buscar certificados

# Shodan (OSINT de dispositivos)
shodan search "org:Target ssl.cert.subject.CN:target.com"

# Google Dorking
site:target.com filetype:pdf
site:target.com inurl:admin
site:target.com intitle:"index of"
```

**REGLA DE ORO:** Nunca escanees sin autorización. Primero lee el scope del programa de bug bounty.

---

## FASE 2: DISCOVERY (descubrir qué hay abierto)

### Escaneo Básico

```bash
# Ping sweep - ¿qué IPs están activas?
nmap -sn 192.168.1.0/24

# Quick scan - los 100 puertos más comunes
nmap 192.168.1.1

# Top 1000 puertos (default)
nmap -T4 192.168.1.1

# Todos los puertos (lento pero completo)
nmap -p- 192.168.1.1

# Rango específico
nmap -p 80,443,8080,8443 192.168.1.1
nmap -p 1-10000 192.168.1.1
```

### Velocidad de Escaneo

```
T0  Paranoia     - 5 minutos por puerto    (evade IDS)
T1  Sneaky       - 15 segundos por puerto  (evade IDS)
T2  Polite       - 0.4 segundos por puerto
T3  Normal       - default
T4  Aggressive   - 15ms por puerto         (RECOMENDADO para auditorías)
T5  Insane       - 5ms por puerto          (puede perder paquetes)
```

**Para auditorías autorizadas:** Usa `-T4`. Para bug bounty con WAF: `-T2` o `-T3`.

---

## FASE 3: ENUMERACIÓN (saber QUÉ corre en cada puerto)

### Service Detection

```bash
# Detectar servicios y versiones
nmap -sV 192.168.1.1

# Detectar SO
nmap -O 192.168.1.1

# Todo junto (servicios + SO + scripts)
nmap -A 192.168.1.1

# Versión específica de cada servicio
nmap -sV --version-intensity 9 192.168.1.1
```

### NSE Scripts (los más útiles para auditorías)

```bash
# Scripts por categoría
nmap --script=default 192.168.1.1      # Scripts básicos
nmap --script=vuln 192.168.1.1         # Detección de vulnerabilidades
nmap --script=auth 192.168.1.1         # Tests de autenticación
nmap --script=discovery 192.168.1.1    # Descubrimiento
nmap --script=exploit 192.168.1.1      # Intentos de explotación (CUIDADO)

# Scripts específicos para web
nmap --script=http-enum 192.168.1.1           # Enumerar directorios
nmap --script=http-headers 192.168.1.1        # Headers HTTP
nmap --script=http-methods 192.168.1.1        # Métodos HTTP permitidos
nmap --script=http-title 192.168.1.1          # Título de la página
nmap --script=http-shellshock 192.168.1.1     # Shellshock vulnerability
nmap --script=http-ssl-cert 192.168.1.1       # Info del certificado SSL

# Scripts para servicios específicos
nmap --script=ssh-auth-methods 192.168.1.1    # Métodos de auth SSH
nmap --script=ftp-anon 192.168.1.1            # FTP anonymous
nmap --script=smb-enum-shares 192.168.1.1     # SMB shares
nmap --script=smb-enum-users 192.168.1.1      # SMB users
nmap --script=mysql-info 192.168.1.1          # MySQL info
nmap --script=ssl-heartbleed 192.168.1.1      # Heartbleed test
nmap --script=ssl-poodle 192.168.1.1          # POODLE test
nmap --script=ssl-enum-ciphers 192.168.1.1    # Cifrados SSL

# Scripts de vulnerabilidad completa
nmap --script="vuln and not (exploit or dos)" 192.168.1.1
```

---

## FASE 4: AUDITORÍA ESPECÍFICA

### Auditoría Web (puertos 80, 443, 8080, 8443)

```bash
# Enumeración web completa
nmap -p 80,443,8080,8443 \
  --script=http-enum,http-headers,http-methods,http-title,http-robots.txt,http-sitemap-generator \
  -sV target.com

# Detectar WAF
nmap -p 80,443 --script=http-waf-detect target.com
nmap -p 80,443 --script=http-waf-fingerprint target.com

# SSL/TLS audit
nmap -p 443 --script=ssl-enum-ciphers,ssl-heartbleed,ssl-poodle,ssl-cert \
  target.com

# Directory bruteforce con NSE
nmap -p 80 --script=http-brute target.com
nmap -p 80 --script=http-wordpress-brute target.com
```

### Auditoría de Red Interna

```bash
# Descubrir hosts activos
nmap -sn 10.0.0.0/24

# Escaneo de puertos TCP
nmap -sS -T4 -p- 10.0.0.0/24

# Escaneo de puertos UDP (los más olvidados)
nmap -sU -T4 --top-ports 20 10.0.0.0/24

# SMB enumeration (Windows)
nmap -p 445 --script=smb-enum-shares,smb-enum-users,smb-os-discovery 10.0.0.0/24

# SNMP enumeration
nmap -sU -p 161 --script=snmp-brute,snmp-info,snmp-sysdescr 10.0.0.0/24

# DNS enumeration
nmap -p 53 --script=dns-brute,dns-zone-transfer 10.0.0.0/24
```

### Auditoría de Wireless

```bash
# Descubrir redes WiFi
nmap --script wireless-wlan-id-info -iL wifi_targets.txt

# WPS testing
nmap -p 8080 --script=http-wifi-brute 192.168.1.1
```

---

## FASE 5: OUTPUT Y REPORTING

### Formatos de Salida

```bash
# XML (para herramientas como Metasploit)
nmap -oX scan_results.xml target.com

# Normal (legible)
nmap -oN scan_results.txt target.com

# Grepable (para scripting)
nmap -oG scan_results.gnmap target.com

# Todos los formatos
nmap -oA scan_results target.com  # Crea .xml, .nmap, .gnmap
```

### Parsing de Resultados

```bash
# Extraer IPs abiertas
grep "Up" scan_results.gnmap | cut -d' ' -f2

# Extraer puertos abiertos
grep "open" scan_results.nmap | grep -v "#"

# Contar servicios
cat scan_results.nmap | grep "open" | awk '{print $3}' | sort | uniq -c | sort -rn

# Importar en Metasploit
msfconsole
db_import scan_results.xml
hosts
services
```

---

## COMANDOS RÁPIDOS PARA AUDITORÍAS

```bash
# Quick audit - todo en uno
nmap -sV -sC -O -p- --min-rate 1000 -oA quick_audit target.com

# Stealth scan (evade algunos IDS)
nmap -sS -T2 -f -D RND:10 target.com

# Web audit completo
nmap -p 80,443,8080,8443,3000,5000,8000,8888 \
  --script="default and http-* and not (http-brute or http-enum)" \
  -sV target.com

# Full TCP + UDP
nmap -sS -sU -T4 -p- --min-rate 1000 target.com

# Vulnerability scan (sin explotar)
nmap -sV --script="vuln and not (exploit or dos)" target.com

# Quick network discovery
nmap -sn 192.168.1.0/24 --max-retries 1 --host-timeout 1000ms
```

---

## SCRIPTS NSE PERSONALIZADOS

### Crear tu propio script

```lua
-- ~/scripts/mi-audit.nse
local nmap = require "nmap"
description = [[
    Mi script de auditoría personalizado
    Escanea puertos comunes y busca vulnerabilidades básicas
]]

categories = {"safe", "discovery"}

action = function(host, port)
    local result = ""
    -- Tu lógica aquí
    return result
end
```

### Uso
```bash
nmap --script=/home/knk/scripts/mi-audit.nse target.com
```

---

## ERRORES COMUNES Y CÓMO EVITARLOS

| Error | Consecuencia | Solución |
|-------|-------------|----------|
| `nmap` sin permisos | No detecta servicios | Usa `sudo` o `--privileged` |
| `-T5` en producción | Pierde paquetes | Usa `-T4` máximo |
| Sin `-sV` | No sabe versiones | Siempre incluir detección de versiones |
| Olvidar UDP | Servicios ocultos | `nmap -sU --top-ports 20` |
| No guardar output | Pierdes resultados | Siempre `-oA nombre` |
| Escanear sin scope | Problemas legales | Lee el scope ANTES de escanear |

---

## REFERENCIA RÁPIDA

```bash
# TCP Scan types
nmap -sT target    # TCP Connect (no necesita root)
nmap -sS target    # TCP SYN (stealth, necesita root)
nmap -sN target    # TCP Null
nmap -sF target    # TCP FIN
nmap -sX target    # TCP Xmas

# UDP
nmap -sU target    # UDP scan

# Output
nmap -oN file target    # Normal
nmap -oX file target    # XML
nmap -oG file target    # Grepable
nmap -oA file target    # All formats

# Performance
nmap -T4 target         # Fast
nmap --min-rate 1000 target  # Minimum packets/sec
nmap --max-retries 2 target # Retries
nmap --host-timeout 30s target  # Timeout per host

# Evasion
nmap -f target          # Fragment packets
nmap -D RND:10 target   # Decoy hosts
nmap -S 1.2.3.4 target  # Spoof source IP
nmap -g 53 target       # Spoof source port
nmap --data-length 25 target  # Random data
```

---

## FLUJO DE AUDITORÍA COMPLETO

```
1. RECON PASIVO        → subfinder, amass, crt.sh, shodan, google dork
2. DISCOVERY           → nmap -sn (hosts) → nmap -p- (puertos)
3. ENUMERACIÓN         → nmap -sV -sC (servicios + scripts)
4. VULNERABILIDAD      → nmap --script=vuln
5. EXPLOTACIÓN         → manual (Metasploit, SQLMap, etc.)
6. POST-EXPLOITACIÓN   → privesc, pivoting, data exfil
7. REPORTE             → findings + evidence + remediation
```

---

## TIPS DE AUDITOR EXPERIMENTADO

1. **Siempre empieza por lo básico** — no necesitas Nuclei si no sabes qué hay abierto
2. **Lee los headers** — mucha info se filtra por headers HTTP
3. **UDP importa** — SNMP, DNS, DHCP pueden tener info valiosa
4. **No confíes en el default** — `nmap -sV --version-intensity 9` detecta más
5. **Guarda TODO** — `nmap -oA` siempre, por si necesitas re-analizar
6. **Velocidad vs precisión** — T4 para audit, T2-T3 para bug bounty con WAF
7. **Scripts = tiempo** — `--script=vuln` puede tardar 30+ minutos
8. **Escanea UDP** — `nmap -sU` al menos los top 20 puertos
9. **Combinar con otras herramientas** — Nmap descubre, Nuclei/Metasploit explota
10. **Documenta cada paso** — tu reporte es tan bueno como tu documentación

---

*Guía creada para knkLx*
*Última actualización: 2026-07-25*
