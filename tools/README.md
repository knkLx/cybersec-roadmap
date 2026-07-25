# PentFlow Toolkit — Tu Suite de Ciberseguridad

## Estructura
```
~/tools/
├── README.md                 # Este archivo
├── start-tor.sh              # Iniciar Tor
├── security-setup.sh         # Configurar seguridad completa
├── GUIDE_PENTFLOW.md         # Guía completa de PentFlow
├── GUIDE_SECURITY.md         # Guía de Tor, Shodan, proxychains
├── GUIDE_WIFI.md             # WiFi sensing (ver a través de paredes)
├── GUIDE_CAMERAS.md          # Cámaras expuestas (legal)
└── GUIDE_FORUMS.md           # Foros, comunidades, cómo ganar dinero

~/pentflow/
├── main.py                   # PentFlow CLI
├── pentflow-tor              # Escanear a través de Tor
└── ...

~/jimmy/
├── jimmy.py                  # Agente autónomo AION SINCRO
└── start.sh                  # Iniciar Jimmy
```

## Inicio Rápido

```bash
# 1. Configurar seguridad
~/tools/security-setup.sh

# 2. Iniciar Tor
~/tools/start-tor.sh

# 3. Escanear con Tor
~/pentflow/pentflow-tor https://target.com

# 4. Usar Jimmy (agente autónomo)
python3 ~/jimmy/jimmy.py "ejecuta: comando"

# 5. Iniciar NOAH (compañero IA)
bash ~/noah/start.sh
```

## Guías

| Guía | Para qué |
|------|----------|
| GUIDE_PENTFLOW.md | Cómo usar PentFlow para bug bounty |
| GUIDE_SECURITY.md | Tor, Shodan, proxychains, firewall |
| GUIDE_WIFI.md | WiFi sensing y detección de presencia |
| GUIDE_CAMERAS.md | Encontrar cámaras expuestas (legal) |
| GUIDE_FORUMS.md | Foros, comunidades, cómo ganar dinero |

## Tus Propósitos

1. **Aprender cybersecurity** → PentFlow + Jimmy + guías
2. **Ganar dinero** → Bug bounty, freelance, CTFs
3. **Proteger tu familia** → Seguridad en tu red
4. **Crear un nodo sostenible** → IA + trabajo humano
5. **Servir de ejemplo** → Compartir tu conocimiento
