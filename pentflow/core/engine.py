"""PentestFlow Engine - Orchestrates the full pentest workflow"""
import asyncio
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Confirm, Prompt

from core.session import Session, Finding, ScanResult
from modules.recon.subdomains import SubdomainEnumerator
from modules.recon.ports import PortScanner
from modules.recon.tech import TechDetector
from modules.recon.endpoints import EndpointDiscovery
from modules.recon.dnsrecon import DNSRecon
from modules.scan.headers import HeaderAnalyzer
from modules.scan.info_disclosure import InfoDisclosureScanner
from modules.scan.vuln_scanner import VulnScanner
from modules.exploit.xss_tester import XSSTester
from modules.exploit.sqli_detector import SQLiDetector
from modules.report.generator import ReportGenerator
from modules.report.github_export import GitHubExporter
from config import VERSION

console = Console()


class PentestEngine:
    def __init__(self, target: str, session: Session = None):
        self.target = target
        self.session = session or Session(target=target)
        self.results = {}
        self.findings = []

    async def run_recon(self):
        console.print("\n[bold cyan]═══ PHASE 1: RECONNAISSANCE ═══[/bold cyan]\n")

        with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(), console=console) as progress:

            # Subdomains
            task = progress.add_task("[cyan]Enumerating subdomains...", total=None)
            enum = SubdomainEnumerator(self.target)
            subs = await enum.enumerate()
            self.results["subdomains"] = subs
            progress.update(task, description=f"[green]Subdomains: {len(subs)} found", completed=1, total=1)

            # DNS
            task = progress.add_task("[cyan]DNS Reconnaissance...", total=None)
            dns = DNSRecon(self.target)
            dns_results = await dns.recon()
            self.results["dns"] = dns_results
            progress.update(task, description=f"[green]DNS records: {len(dns_results.get('records', {}))}", completed=1, total=1)

            # Ports
            task = progress.add_task("[cyan]Scanning ports...", total=None)
            scanner = PortScanner(self.target)
            ports = await scanner.scan()
            self.results["ports"] = ports
            progress.update(task, description=f"[green]Open ports: {len(ports)}", completed=1, total=1)

            # Tech
            task = progress.add_task("[cyan]Detecting technologies...", total=None)
            tech = TechDetector(self.target)
            techs = await tech.detect()
            self.results["technologies"] = techs
            progress.update(task, description=f"[green]Technologies: {len(techs)}", completed=1, total=1)

            # Endpoints
            task = progress.add_task("[cyan]Discovering endpoints...", total=None)
            ep = EndpointDiscovery(self.target)
            endpoints = await ep.discover(subdomains=subs)
            self.results["endpoints"] = endpoints
            progress.update(task, description=f"[green]Endpoints: {len(endpoints)}", completed=1, total=1)

        self._display_recon_results()
        self.session.phases["recon"] = "completed"
        self.session.save()

    def _display_recon_results(self):
        if self.results.get("subdomains"):
            table = Table(title="Subdomains", show_header=True, header_style="bold cyan")
            table.add_column("#", style="dim")
            table.add_column("Subdomain")
            for i, s in enumerate(self.results["subdomains"][:50], 1):
                table.add_row(str(i), s)
            console.print(table)

        if self.results.get("ports"):
            table = Table(title="Open Ports", show_header=True, header_style="bold cyan")
            table.add_column("Port")
            table.add_column("State", style="green")
            table.add_column("Service")
            for p in self.results["ports"]:
                table.add_row(str(p["port"]), p["state"], p.get("service", "?"))
            console.print(table)

        if self.results.get("technologies"):
            table = Table(title="Technologies", show_header=True, header_style="bold cyan")
            table.add_column("Technology", style="magenta")
            for t in self.results["technologies"]:
                table.add_row(t)
            console.print(table)

    async def run_scan(self):
        console.print("\n[bold yellow]═══ PHASE 2: VULNERABILITY SCANNING ═══[/bold yellow]\n")

        with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(), console=console) as progress:

            # Header analysis
            task = progress.add_task("[yellow]Analyzing security headers...", total=None)
            headers = HeaderAnalyzer(self.target)
            header_findings = await headers.analyze()
            for f in header_findings:
                self.session.add_finding(f)
            progress.update(task, description=f"[green]Header findings: {len(header_findings)}", completed=1, total=1)

            # Info disclosure
            task = progress.add_task("[yellow]Checking information disclosure...", total=None)
            info = InfoDisclosureScanner(self.target)
            info_findings = await info.scan(endpoints=self.results.get("endpoints", []))
            for f in info_findings:
                self.session.add_finding(f)
            progress.update(task, description=f"[green]Info disclosure: {len(info_findings)}", completed=1, total=1)

            # Vulnerability scanner
            task = progress.add_task("[yellow]Running vulnerability scans...", total=None)
            vuln = VulnScanner(self.target)
            vuln_findings = await vuln.scan(
                endpoints=self.results.get("endpoints", []),
                technologies=self.results.get("technologies", []),
            )
            for f in vuln_findings:
                self.session.add_finding(f)
            progress.update(task, description=f"[green]Vulnerabilities: {len(vuln_findings)}", completed=1, total=1)

        self.session.phases["scan"] = "completed"
        self.session.save()

    async def run_exploit(self, auto: bool = True):
        console.print("\n[bold red]═══ PHASE 3: EXPLOITATION ═══[/bold red]\n")

        if not auto:
            try:
                if not Confirm.ask("[yellow]Run exploitation tests? (requires authorization)[/yellow]"):
                    console.print("[dim]Skipping exploitation phase[/dim]")
                    return
            except EOFError:
                console.print("[dim]Non-interactive, skipping exploit[/dim]")
                return

        with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(), console=console) as progress:

            # XSS
            task = progress.add_task("[red]Testing XSS vulnerabilities...", total=None)
            xss = XSSTester(self.target)
            xss_findings = await xss.test(endpoints=self.results.get("endpoints", []))
            for f in xss_findings:
                self.session.add_finding(f)
            progress.update(task, description=f"[green]XSS findings: {len(xss_findings)}", completed=1, total=1)

            # SQLi
            task = progress.add_task("[red]Testing SQL injection...", total=None)
            sqli = SQLiDetector(self.target)
            sqli_findings = await sqli.detect(endpoints=self.results.get("endpoints", []))
            for f in sqli_findings:
                self.session.add_finding(f)
            progress.update(task, description=f"[green]SQLi findings: {len(sqli_findings)}", completed=1, total=1)

        self.session.phases["exploit"] = "completed"
        self.session.save()

    def generate_report(self, format: str = "markdown"):
        console.print("\n[bold green]═══ PHASE 4: REPORT GENERATION ═══[/bold green]\n")
        gen = ReportGenerator(self.session, self.results)
        report_path = gen.generate(format=format)
        console.print(f"[green]Report saved: {report_path}[/green]")
        self.session.phases["report"] = "completed"
        self.session.save()
        return report_path

    def export_to_github(self, repo_name: str = None):
        console.print("\n[bold blue]═══ PHASE 5: GITHUB EXPORT ═══[/bold blue]\n")
        exporter = GitHubExporter(self.session, self.results)
        repo_url = exporter.export(repo_name=repo_name)
        if repo_url:
            self.session.github_repo = repo_url
            self.session.save()
            console.print(f"[green]Exported to: {repo_url}[/green]")
        return repo_url

    def display_summary(self):
        summary = self.session.summary()
        table = Table(title="Session Summary", show_header=True, header_style="bold")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Target", summary["target"])
        table.add_row("Session", summary["session_id"])
        table.add_row("Status", summary["status"])
        table.add_row("Total Findings", str(summary["total_findings"]))
        table.add_row("Critical", f"[red]{summary['critical']}[/red]")
        table.add_row("High", f"[yellow]{summary['high']}[/yellow]")
        table.add_row("Medium", f"[orange3]{summary['medium']}[/orange3]")
        table.add_row("Low", f"[blue]{summary['low']}[/blue]")
        table.add_row("Info", f"[dim]{summary['info']}[/dim]")
        console.print(table)

    async def run_full(self):
        banner = f"""
[bold cyan]
╔══════════════════════════════════════════════════════╗
║           PentFlow v{VERSION}                        ║
║           Automated Bug Bounty Framework            ║
╚══════════════════════════════════════════════════════╝
[/bold cyan]
[bold white]Target: {self.target}[/bold white]
[bold white]Session: {self.session.session_id}[/bold white]
"""
        console.print(banner)

        await self.run_recon()
        await self.run_scan()
        await self.run_exploit(auto=True)
        report = self.generate_report()
        self.display_summary()

        return report

    async def run_phase(self, phase: str):
        phases = {
            "recon": self.run_recon,
            "scan": self.run_scan,
            "exploit": self.run_exploit,
            "report": lambda: self.generate_report(),
        }
        if phase in phases:
            result = phases[phase]()
            if asyncio.iscoroutine(result):
                await result
            return result
        console.print(f"[red]Unknown phase: {phase}[/red]")
