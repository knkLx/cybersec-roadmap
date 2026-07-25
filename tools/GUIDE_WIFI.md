# WiFi Sensing — Ver a través de paredes con WiFi

## Qué es
WiFi sensing usa las señales WiFi para detectar presencia humana, movimiento, y actividad. No es como en las películas — no ves imágenes, pero puedes detectar:

- Si hay alguien en una habitación
- Movimiento y gestos
- Respiración y ritmo cardíaco (en investigación)
- Patrones de actividad

## Hardware Necesario

### Opción 1: Router WiFi con soporte CSI (~$50-100)
- ESP32 con soporte CSI (Channel State Information)
- Router con OpenWrt compatible
- Raspberry Pi 4+ con WiFi adapter

### Opción 2: mmWave Radar Kit (~$200-500)
- TI IWR1443BOOST
- Google Soli radar
- Huawei WiFi Sensing API

### Opción 3: Solo software (gratis, limitado)
- Usar tu router actual con scripts de análisis
- No tan preciso pero funciona para detectar presencia

## Instalación (Software)

### Wi-Sense (Detección de presencia)
```bash
cd ~/tools
git clone https://github.com/RiceD2Lab/Wi-Sense.git
cd Wi-Sense
pip install -r requirements.txt
```

### WiFi CSI Analyzer
```bash
pip install matplotlib numpy scipy scapy
```

### Scripts Básicos de Detección
```python
#!/usr/bin/env python3
"""
WiFi Presence Detector — Detecta dispositivos en la red
"""
import subprocess
import re
import time

def scan_network():
    """Escanea la red WiFi local"""
    result = subprocess.run(['iwlist', 'wlan0', 'scan'], capture_output=True, text=True)
    cells = re.findall(r'Cell \d+ - Address: ([\w:]+)', result.stdout)
    return cells

def arp_scan():
    """ARP scan para ver dispositivos en la red"""
    result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
    return result.stdout

def monitor_signal():
    """Monitorea cambios en señal WiFi"""
    print("[*] Monitoring WiFi signals... (Ctrl+C to stop)")
    seen = {}
    try:
        while True:
            cells = scan_network()
            for cell in cells:
                if cell not in seen:
                    seen[cell] = time.time()
                    print(f"[NEW DEVICE] {cell}")
            time.sleep(5)
    except KeyboardInterrupt:
        print(f"\n[*] Total devices seen: {len(seen)}")

if __name__ == "__main__":
    print("=== WiFi Presence Detector ===")
    print("1. Network scan")
    print("2. ARP scan")
    print("3. Monitor signals")
    choice = input("Select: ")

    if choice == "1":
        devices = scan_network()
        print(f"Found {len(devices)} devices")
        for d in devices:
            print(f"  - {d}")
    elif choice == "2":
        print(arp_scan())
    elif choice == "3":
        monitor_signal()
```

## Investigación Real

### Papers Importantes
1. **"Wi-Sense"** — WiFi-based human sensing (Rice University)
2. **"WiGAN"** — WiFi image generation
3. **"RF-Pose"** — MIT, radar for human pose estimation
4. **"TensorFi"** — WiFi sensing with deep learning

### Proyectos Open Source
- https://github.com/RiceD2Lab/Wi-Sense
- https://github.com/RiceD2Lab/WiGAN
- https://github.com/WiSig
- https://github.com/SenseFi

## Limitaciones Reales

| Lo que SÍ puede hacer | Lo que NO puede hacer |
|----------------------|----------------------|
| Detectar presencia en habitación | Ver a través de paredes |
| Contar personas | Ver caras o detalles |
| Detectar movimiento | Ver en tiempo real como video |
| Monitorear actividad | Espiar conversaciones |
| Detección de respiración | Reemplazar una cámara |

## Uso Ético

- **Investigación** en tu propia red
- **Hogar inteligente** (detectar si alguien está en casa)
- **Seguridad** (detectar intrusos)
- **Salud** (monitoreo de pacientes — research)
- **NO para espionaje** — esto es ilegal
