# Cámara Scanning — Encontrar cámaras expuestas (Legal)

## IMPORTANTE: ÉTICA Y LEGALIDAD

### Lo que es LEGAL
- Identificar cámaras IP expuestas en internet
- Reportar vulnerabilidades a los fabricantes
- Escanear tus propias cámaras
- Bug bounty en programas IoT

### Lo que es ILEGAL
- Acceder a cámaras que no son tuyas
- Grabar o mirar el feed de cámaras ajenas
- Usar cámaras comprometidas para atacar
- Cualquier uso sin autorización

### Consecuencias
- En España: hasta 3 años de prisión (Ley Orgánica 3/2018)
- En USA: Computer Fraud and Abuse Act (hasta 20 años)
- En la UE: GDPR + leyes nacionales de ciberseguridad

## Herramientas Legales

### 1. SHODAN (ya instalado)
```bash
# Buscar cámaras RTSP
shodan search "port:554 has_screenshot:true" --limit 20

# Buscar cámaras en España
shodan search "port:554 country:ES" --limit 10

# Buscar cámaras con default creds
shodan search "port:554 default password" --limit 10

# Info de un host específico
shodan host 123.456.789.0
```

### 2. CENSYS
```bash
pip install censys
censys search "services.port=554"
```

### 3. Nmap (para tus propias cámaras)
```bash
# Escanear tu red local
nmap -sV -p 554,80,8080,8443 192.168.1.0/24

# Buscar RTSP
nmap -p 554 --script rtsp-url-brute 192.168.1.0/24
```

### 4. Scripts de Detección
```python
#!/usr/bin/env python3
"""
Camera Scanner — Detecta cámaras IP en tu red
SOLO para uso en tu propia red
"""
import socket
import concurrent.futures

RTSP_PORTS = [554, 8554, 1554]
HTTP_PORTS = [80, 8080, 8443, 443]

def check_port(ip, port, timeout=2):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def scan_network(subnet="192.168.1"):
    """Escanea tu red local para cámaras"""
    print(f"[*] Scanning {subnet}.0/24 for cameras...")
    open_hosts = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {}
        for i in range(1, 255):
            ip = f"{subnet}.{i}"
            for port in RTSP_PORTS + HTTP_PORTS:
                future = executor.submit(check_port, ip, port)
                futures[future] = (ip, port)

        for future in concurrent.futures.as_completed(futures):
            ip, port = futures[future]
            if future.result():
                open_hosts.append((ip, port))
                print(f"  [OPEN] {ip}:{port}")

    return open_hosts

if __name__ == "__main__":
    subnet = input("Subnet (default 192.168.1): ") or "192.168.1"
    hosts = scan_network(subnet)
    print(f"\n[*] Found {len(hosts)} open ports")
    print("[*] These could be cameras. Verify manually.")
    print("[*] Do NOT access cameras you don't own.")
```

## Cámaras Comunes y Sus Credenciales Default

### Solo para testing en tus propias cámaras

| Marca | Puerto | Usuario | Contraseña |
|-------|--------|---------|------------|
| Hikvision | 80/554 | admin | admin123 |
| Dahua | 80/554 | admin | admin |
| Axis | 80 | root | pass |
| Foscam | 80 | admin | (vacía) |
| TP-Link | 80 | admin | admin |
| Reolink | 80 | admin | admin |

### IMPORTANTE
- **Solo usa estas credenciales en tus propias cámaras**
- Si encuentras una cámara con default creds en internet → **repórtala**
- Muchos fabricantes tienen programa de bug bounty

## Cómo Reportar Cámaras Expuestas

### Si es una vulnerabilidad real
1. Identifica el fabricante (Hikvision, Dahua, etc.)
2. Ve a su programa de bug bounty o security contact
3. Reporta: "Cámara IP con credenciales default en [IP]"
4. No incluyas screenshots con personas visibles

### Si no hay programa de bug bounty
1. Contacta al ISP del IP
2. Reporta al CERT national (cert@es)
3. Usa responsible disclosure

## Bug Bounty en IoT

### Programas que pagan por IoT vulns
| Programa | Tipo | Bounty |
|----------|------|--------|
| General Motors | IoT/Vehicle | $100-$10,000 |
| AT&T | IoT/Network | $150-$5,000 |
| Honeywell | IoT/Home | Variable |
| Ring (Amazon) | Cameras | Variable |
| Nest (Google) | Cameras | Variable |

### Qué buscar en IoT
- Default credentials
- Hardcoded API keys
- Insecure firmware updates
- Exposed management interfaces
- Cleartext protocols (RTSP, Telnet)
- Weak authentication
