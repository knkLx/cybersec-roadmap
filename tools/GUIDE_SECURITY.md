# Guía de Seguridad — Tor, Shodan, WiFi Tools

## TU SETUP SEGURO

### Estructura
```
~/tools/
├── start-tor.sh          # Iniciar Tor
├── security-setup.sh     # Configurar seguridad completa
├── GUIDE_PENTFLOW.md     # Guía de PentFlow
├── GUIDE_NOVA.md         # Guía de NOVA
├── GUIDE_SECURITY.md     # Esta guía
├── GUIDE_WIFI.md         # Guía WiFi sensing
└── GUIDE_CAMERAS.md      # Guía de cámara scanning
```

---

## 1. TOR — Anonimato

### Qué es
Tor routes your traffic through 3 random nodes worldwide. Nobody sees your real IP.

### Instalar
```bash
# Ya instalado via conda
export PATH="$HOME/.miniforge/bin:$PATH"
```

### Iniciar Tor
```bash
~/tools/start-tor.sh
```

### Verificar que funciona
```bash
# Test your Tor IP
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip

# Debe retornar una IP diferente a la tuya
```

### Usar Tor con PentFlow
```bash
# Método 1: Wrapper automático
~/pentflow/pentflow-tor https://target.com

# Método 2: proxychains
proxychains4 python3 main.py https://target.com

# Método 3: torsocks
torsocks python3 main.py https://target.com
```

### Usar Tor con otros tools
```bash
# Navegador
torsocks firefox

# Cualquier comando
torsocks curl https://target.com
torsocks nmap -sT target.com
```

### Cambiar IP de Tor
```bash
# Reiniciar Tor para nueva identidad
killall tor
tor &
sleep 5
```

### Configuración avanzada
```bash
# Editar ~/.tor/torrc para:
# - ExitNodes: países específicos
# - StrictNodes: forzar solo esos países
# - SocksPort: cambiar puerto

# Ejemplo: solo salir por España
ExitNodes {es}
StrictNodes 1
```

---

## 2. SHODAN — Motor de Búsqueda IoT

### Qué es
Shodan indexa dispositivos IoT, cámaras, servidores, SCADA, etc. Es como Google pero para dispositivos.

### Instalar
```bash
pip install shodan
```

### Configurar
```bash
# Crear cuenta gratis en shodan.io
# Obtener API key
shodan init TU_API_KEY
```

### Comandos Básicos

```bash
# Buscar servidores web con screenshots
shodan search "has_screenshot:true port:443" --limit 10

# Buscar cámaras RTSP
shodan search "port:554 has_screenshot:true" --limit 20

# Buscar en tu país
shodan search "country:ES port:22" --limit 10

# Buscar por org
shodan search "org:'Amazon' port:80" --limit 10

# Info de un host
shodan host 8.8.8.8

# Buscar con facets (estadísticas)
shodan search "apache" --facets port:10
```

### Desde Python
```python
import shodan

api = shodan.Shodan('TU_API_KEY')

# Buscar
results = api.search('port:22 country:ES')
for result in results['matches']:
    print(f"IP: {result['ip_str']}")
    print(f"Data: {result['data'][:100]}")
    print("---")

# Info de host
host = api.host('8.8.8.8')
for item in host['data']:
    print(f"Port: {item['port']}")
    print(f"Banner: {item['data'][:100]}")
```

### Lo que puedes buscar (legalmente)
- Servidores con default credentials
- Cámaras IP expuestas (y reportarlas)
- Bases de datos sin auth
- Dispositivos SCADA/ICS
- Printers expuestas

### IMPORTANTE
- **Identificar** es legal
- **Acceder** sin autorización es ILEGAL
- Si encuentras algo vulnerable, **reporta** al vendor
- No uses Shodan para atacar

---

## 3. CENSYS — Alternativa a Shodan

### Web
```
https://censys.io
```

### API
```bash
pip install censys
censys config  # Configurar API keys
censys search "services.port=443 and services.tls.certificates.leaf.names=shopify.com"
```

---

## 4. PROXYCHAINS — Tor para cualquier tool

### Configurar
```bash
# Editar ~/.proxychains/proxychains.conf
strict_chain
proxy_dns
[ProxyList]
socks5 127.0.0.1 9050
```

### Usar
```bash
proxychains4 nmap -sT target.com
proxychains4 python3 main.py target.com
proxychains4 nikto -h target.com
proxychains4 dirb http://target.com
```

### Modos
- `strict_chain`: Todo va por Tor (seguro, lento)
- `random_chain`: Rutas aleatorias (menos seguro)
- `dynamic_chain`: Usa Tor si puede, si no directo

---

## 5. MACCHANGER — Anti-fingerprinting

### Instalar
```bash
sudo apt install macchanger
```

### Usar
```bash
# Ver MAC actual
macchanger -s wlan0

# Cambiar MAC aleatoria
sudo ip link set wlan0 down
sudo macchanger -r wlan0
sudo ip link set wlan0 up

# Volver a MAC original
sudo ip link set wlan0 down
sudo macchanger -p wlan0
sudo ip link set wlan0 up
```

### Auto-cambiar al iniciar
```bash
# Agregar a /etc/network/if-up.d/macchanger
sudo nano /etc/network/if-up.d/macchanger
```

---

## 6. FIREWALL (UFW)

### Configurar
```bash
# Habilitar
sudo ufw enable

# Reglas básicas
sudo ufw default deny outgoing
sudo ufw default deny incoming
sudo ufw allow out 443/tcp    # HTTPS
sudo ufw allow out 53/udp     # DNS
sudo ufw allow out 9050/tcp   # TOR
sudo ufw allow out 22/tcp     # SSH (si necesitas)

# Ver estado
sudo ufw status verbose
```

---

## CHECKLIST DE SEGURIDAD ANTES DE ESCANEAR

- [ ] Tor activo y funcionando
- [ ] IP verificada (check.torproject.org)
- [ ] Scope del programa leído
- [ ] Rate limiting configurado
- [ ] Logs activados
- [ ] No datos sensibles en el scan
- [ ] Report listo para enviar

---

## COMANDOS RÁPIDOS

```bash
# Iniciar todo
~/tools/start-tor.sh

# Verificar Tor
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip

# Escanear con Tor
~/pentflow/pentflow-tor https://target.com

# Buscar en Shodan
shodan search "port:22 country:ES" --limit 10

# Cambiar MAC
sudo macchanger -r wlan0

# Ver firewall
sudo ufw status
```
