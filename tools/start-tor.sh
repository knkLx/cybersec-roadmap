#!/bin/bash
# PentFlow Tor Setup — Run this before any scan
# Creates a transparent proxy through Tor

export PATH="$HOME/.miniforge/bin:$PATH"

echo "[*] Starting Tor..."
tor &
sleep 5

echo "[*] Testing Tor connection..."
curl --socks5-hostname 127.0.0.1:9050 -s https://check.torproject.org/api/ip 2>&1

echo ""
echo "[*] Tor is running on port 9050"
echo "[*] To use: torsocks python3 main.py target.com"
echo "[*] Or: proxychains python3 main.py target.com"
echo ""
echo "[*] To stop: killall tor"
