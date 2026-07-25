from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def print_banner():
    banner = """
[bold red]
    ╔═══════════════════════════════════╗
    ║   ReconX - Recon Automation      ║
    ║   Bug Bounty Toolkit             ║
    ╚═══════════════════════════════════╝
[/bold red]"""
    console.print(banner)

def print_subdomains(subdomains: list[str], domain: str):
    table = Table(title=f"Subdomains found for {domain}")
    table.add_column("#", style="cyan")
    table.add_column("Subdomain", style="green")
    for i, sub in enumerate(subdomains, 1):
        table.add_row(str(i), sub)
    console.print(table)

def print_ports(ports: list[dict], target: str):
    table = Table(title=f"Open Ports - {target}")
    table.add_column("Port", style="cyan")
    table.add_column("State", style="green")
    table.add_column("Service", style="yellow")
    for p in ports:
        table.add_row(str(p["port"]), p["state"], p.get("service", "?"))
    console.print(table)

def print_tech(techs: list[str], target: str):
    table = Table(title=f"Technologies - {target}")
    table.add_column("Technology", style="magenta")
    for t in techs:
        table.add_row(t)
    console.print(table)

def print_endpoints(endpoints: list[str], target: str):
    table = Table(title=f"Endpoints - {target}")
    table.add_column("#", style="cyan")
    table.add_column("URL", style="green")
    for i, ep in enumerate(endpoints, 1):
        table.add_row(str(i), ep)
    console.print(table)
