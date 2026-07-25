#!/usr/bin/env python3
"""
ReconX - Recon Automation Toolkit for Bug Bounty
"""

import asyncio
import argparse
import json
from datetime import datetime
from pathlib import Path

from recon.subdomains import enumerate as subdomain_enum
from recon.ports import scan as port_scan
from recon.tech import detect as tech_detect
from recon.endpoints import discover as endpoint_discover
from utils.output import (
    console, print_banner, print_subdomains,
    print_ports, print_tech, print_endpoints,
)
from utils.config import REPORTS_DIR, VERSION


def save_report(target: str, data: dict):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = REPORTS_DIR / f"{target}_{ts}.json"
    with open(report, "w") as f:
        json.dump(data, f, indent=2)
    console.print(f"\n[bold green][+][/bold green] Report saved: {report}")


async def run_full(target: str):
    console.print(f"\n[bold yellow][*] Target:[/bold yellow] {target}\n")

    # Subdomains
    console.print("[bold cyan][>] Enumerating subdomains...[/bold cyan]")
    subdomains = await subdomain_enum(target)
    print_subdomains(subdomains, target)
    console.print(f"    Found {len(subdomains)} subdomains\n")

    # Ports
    console.print("[bold cyan][>] Scanning ports...[/bold cyan]")
    ports = await port_scan(target)
    print_ports(ports, target)
    console.print(f"    Found {len(ports)} open ports\n")

    # Tech
    console.print("[bold cyan][>] Detecting technologies...[/bold cyan]")
    techs = await tech_detect(target)
    print_tech(techs, target)
    console.print(f"    Detected {len(techs)} technologies\n")

    # Endpoints
    console.print("[bold cyan][>] Discovering endpoints...[/bold cyan]")
    endpoints = await endpoint_discover(target)
    print_endpoints(endpoints, target)
    console.print(f"    Found {len(endpoints)} endpoints\n")

    # Save report
    save_report(target, {
        "target": target,
        "timestamp": datetime.now().isoformat(),
        "subdomains": subdomains,
        "ports": ports,
        "technologies": techs,
        "endpoints": endpoints,
    })


async def main():
    parser = argparse.ArgumentParser(description="ReconX - Recon Automation Toolkit")
    parser.add_argument("target", nargs="?", help="Target domain or URL")
    parser.add_argument("-s", "--subdomains", action="store_true", help="Subdomain enumeration only")
    parser.add_argument("-p", "--ports", action="store_true", help="Port scan only")
    parser.add_argument("-t", "--tech", action="store_true", help="Tech detection only")
    parser.add_argument("-e", "--endpoints", action="store_true", help="Endpoint discovery only")
    parser.add_argument("-v", "--version", action="version", version=f"ReconX {VERSION}")
    parser.add_argument("-o", "--output", help="Output file (JSON)")

    args = parser.parse_args()

    if not args.target:
        print_banner()
        parser.print_help()
        return

    print_banner()

    target = args.target.rstrip("/")

    if args.subdomains:
        subs = await subdomain_enum(target)
        print_subdomains(subs, target)
        if args.output:
            Path(args.output).write_text(json.dumps(subs, indent=2))
    elif args.ports:
        ports = await port_scan(target)
        print_ports(ports, target)
        if args.output:
            Path(args.output).write_text(json.dumps(ports, indent=2))
    elif args.tech:
        techs = await tech_detect(target)
        print_tech(techs, target)
        if args.output:
            Path(args.output).write_text(json.dumps(techs, indent=2))
    elif args.endpoints:
        eps = await endpoint_discover(target)
        print_endpoints(eps, target)
        if args.output:
            Path(args.output).write_text(json.dumps(eps, indent=2))
    else:
        await run_full(target)


if __name__ == "__main__":
    asyncio.run(main())
