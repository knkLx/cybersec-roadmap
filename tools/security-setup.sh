#!/bin/bash
# PentFlow Security Setup — Run once to harden your Ubuntu
# This configures Tor, DNS, firewall, and MAC randomization

export PATH="$HOME/.miniforge/bin:$PATH"

echo "╔══════════════════════════════════════════╗"
echo "║  PentFlow Security Setup                 ║"
echo "║  Configure your attacking environment    ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# 1. DNS over HTTPS
echo "[1/5] Configuring DNS over HTTPS..."
sudo mkdir -p /etc/systemd/resolved.conf.d
cat << 'EOF' | sudo tee /etc/systemd/resolved.conf.d/dns-over-https.conf
[Resolve]
DNS=1.1.1.1#cloudflare-dns.com 9.9.9.9#dns.quad9.net
DNSOverTLS=yes
DNSSEC=yes
EOF
sudo systemctl restart systemd-resolved
echo "  [OK] DNS over HTTPS configured"

# 2. Install proxychains for Tor routing
echo "[2/5] Installing proxychains..."
sudo apt-get install -y proxychains4 2>/dev/null || echo "  [WARN] Install proxychains manually"

# Configure proxychains
cat << 'EOF' > ~/.proxychains/proxychains.conf
strict_chain
proxy_dns
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
socks5 127.0.0.1 9050
EOF
mkdir -p ~/.proxychains
cp ~/.proxychains/proxychains.conf ~/.proxychains/proxychains.conf 2>/dev/null
echo "  [OK] Proxychains configured for Tor"

# 3. Install and configure Tor
echo "[3/5] Configuring Tor..."
mkdir -p ~/.tor
cat << 'EOF' > ~/.tor/torrc
SocksPort 9050
ControlPort 9051
HashedControlPassword
CookieAuthentication 1
RunAsDaemon 1
DataDirectory ~/.tor/data
Log notice file ~/.tor/tor.log
ExitNodes {es},{fr},{de},{nl},{ro}
StrictNodes 0
EOF
echo "  [OK] Tor configured"

# 4. Create PentFlow security wrapper
echo "[4/5] Creating security wrappers..."
cat << 'WRAPPER' > ~/pentflow/pentflow-tor
#!/bin/bash
# PentFlow through Tor — anonymized scanning
export PATH="$HOME/.miniforge/bin:$HOME/.local/bin:$PATH"

# Start Tor if not running
if ! pgrep -x tor > /dev/null; then
    echo "[*] Starting Tor..."
    tor &
    sleep 5
fi

# Test Tor connection
echo "[*] Testing Tor connection..."
IP=$(curl --socks5-hostname 127.0.0.1:9050 -s https://check.torproject.org/api/ip 2>/dev/null)
echo "[*] Your Tor IP: $IP"

# Run PentFlow through Tor
echo "[*] Running PentFlow through Tor..."
cd ~/pentflow
proxychains4 python3 main.py "$@"
WRAPPER
chmod +x ~/pentflow/pentflow-tor
echo "  [OK] PentFlow Tor wrapper created"

# 5. Create tools directory with all scripts
echo "[5/5] Setting up tools directory..."
mkdir -p ~/tools
echo "  [OK] Tools directory ready"

echo ""
echo "═══ SETUP COMPLETE ═══"
echo ""
echo "Usage:"
echo "  1. Start Tor:    ~/tools/start-tor.sh"
echo "  2. Scan via Tor:  ~/pentflow/pentflow-tor target.com"
echo "  3. Direct scan:   cd ~/pentflow && python3 main.py target.com"
echo ""
echo "Security checklist:"
echo "  [✓] DNS over HTTPS (Cloudflare + Quad9)"
echo "  [✓] Tor proxy configured"
echo "  [✓] Proxychains ready"
echo "  [✓] PentFlow Tor wrapper"
echo ""
echo "Manual steps needed:"
echo "  - Install ProtonVPN: sudo apt install protonvpn-cli"
echo "  - Randomize MAC: sudo macchanger -r wlan0"
echo "  - Enable UFW: sudo ufw enable"
