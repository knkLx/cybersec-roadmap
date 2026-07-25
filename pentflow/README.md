# PentFlow

Automated Bug Bounty Framework — Professional pentest & audit automation with step-by-step workflow.

## Features

- **Full Recon Pipeline** — Subdomains, ports, tech fingerprinting, endpoints, DNS recon
- **Vulnerability Scanning** — Security headers, info disclosure, CORS, clickjacking, open redirect
- **Exploitation** — XSS detection, SQL injection detection
- **Session Management** — Save/resume pentest progress
- **Professional Reports** — Markdown and HTML reports with severity classification
- **GitHub Integration** — Auto-push reports to GitHub repos
- **Interactive CLI** — Step-by-step guided pentest workflow

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Interactive Mode (Recommended)
```bash
python main.py -i
```

### Full Scan
```bash
python main.py example.com
```

### Single Phase
```bash
python main.py example.com -p recon
python main.py example.com -p scan
python main.py example.com -p exploit
python main.py example.com -p report
```

### Resume Session
```bash
python main.py example.com -s <session_id>
```

### List Sessions
```bash
python main.py --list
```

### Export to GitHub
```bash
python main.py --export <session_id>
```

## Workflow

```
Phase 1: RECONNAISSANCE
  ├── Subdomain enumeration (crt.sh, AlienVault, ThreatCrowd, DNS brute)
  ├── DNS reconnaissance (zone transfer, wildcard detection)
  ├── Port scanning (async, 30+ common ports)
  ├── Technology fingerprinting (20+ signatures)
  └── Endpoint discovery (40+ common paths)

Phase 2: VULNERABILITY SCANNING
  ├── Security header analysis (7 headers)
  ├── Information disclosure (20+ sensitive paths)
  ├── CORS misconfiguration
  ├── Clickjacking
  ├── Open redirect
  └── Sensitive endpoint detection

Phase 3: EXPLOITATION
  ├── XSS testing (reflected, stored indicators)
  └── SQL injection detection (error-based, time-based, content-based)

Phase 4: REPORTING
  ├── Markdown report
  ├── HTML report (dark theme)
  └── GitHub export
```

## Severity Levels

| Level | Description |
|-------|-------------|
| CRITICAL | Immediate risk, requires urgent attention |
| HIGH | Significant vulnerability, should be fixed soon |
| MEDIUM | Moderate risk, recommended to fix |
| LOW | Minor issue, best practice improvement |
| INFO | Informational finding, no direct risk |

## Project Structure

```
pentestflow/
├── main.py              # CLI entry point
├── config.py            # Configuration
├── core/
│   ├── engine.py        # Main orchestration engine
│   └── session.py       # Session management
├── modules/
│   ├── recon/           # Reconnaissance modules
│   │   ├── subdomains.py
│   │   ├── ports.py
│   │   ├── tech.py
│   │   ├── endpoints.py
│   │   └── dnsrecon.py
│   ├── scan/            # Vulnerability scanning
│   │   ├── headers.py
│   │   ├── info_disclosure.py
│   │   └── vuln_scanner.py
│   ├── exploit/         # Exploitation
│   │   ├── xss_tester.py
│   │   └── sqli_detector.py
│   └── report/          # Report generation
│       ├── generator.py
│       └── github_export.py
├── reports/             # Generated reports
├── sessions/            # Saved sessions
└── requirements.txt
```

## Important

This tool is for **authorized security testing only**. Always obtain explicit written authorization before testing any target. Use responsibly and ethically.

## License

MIT
