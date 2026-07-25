#!/usr/bin/env python3
"""
PentFlow - Automated Bug Bounty Framework
Professional pentest automation with step-by-step workflow
"""
import asyncio
import sys
import argparse
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

from core.engine import PentestEngine
from core.session import Session
from config import VERSION

console = Console()


def print_banner():
    banner = f"""
[bold cyan]
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ██████╗ ███████╗████████╗██████╗  ██████╗                  ║
║   ██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔═══██╗                 ║
║   ██████╔╝█████╗     ██║   ██████╔╝██║   ██║                 ║
║   ██╔═══╝ ██╔══╝     ██║   ██╔═══╝ ██║   ██║                 ║
║   ██║     ███████╗   ██║   ██║     ╚██████╔╝                 ║
║   ╚═╝     ╚══════╝   ╚═╝   ╚═╝      ╚═════╝                  ║
║                                                              ║
║   PentFlow v{VERSION}                                          ║
║   Automated Bug Bounty Framework                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
[/bold cyan]"""
    console.print(banner)


def list_sessions():
    sessions = Session.list_sessions()
    if not sessions:
        console.print("[dim]No sessions found[/dim]")
        return

    table = Table(title="Sessions", show_header=True, header_style="bold cyan")
    table.add_column("Session ID")
    table.add_column("Target")
    table.add_column("Status")
    table.add_column("Findings")
    table.add_column("Created")

    for s in sessions:
        status_color = {"active": "green", "completed": "blue", "paused": "yellow"}.get(s["status"], "white")
        table.add_row(
            s["session_id"],
            s["target"],
            f"[{status_color}]{s['status']}[/{status_color}]",
            str(s["findings"]),
            s["created_at"][:19],
        )
    console.print(table)


async def run_full_scan(target: str, session_id: str = None):
    session = Session(target=target)
    if session_id:
        try:
            session = Session.load(session_id)
            console.print(f"[green]Resumed session: {session_id}[/green]")
        except FileNotFoundError:
            console.print(f"[yellow]Session not found, creating new one[/yellow]")

    engine = PentestEngine(target, session)
    report = await engine.run_full()

    console.print(f"\n[bold green]Scan complete![/bold green]")
    console.print(f"[dim]Report: {report}[/dim]")
    console.print(f"[dim]Session: {session.session_id}[/dim]")

    try:
        if Confirm.ask("\n[bold]Export to GitHub?[/bold]"):
            engine.export_to_github()
    except EOFError:
        pass

    return report


async def run_phase(target: str, phase: str, session_id: str = None):
    session = Session(target=target)
    if session_id:
        try:
            session = Session.load(session_id)
        except FileNotFoundError:
            pass

    engine = PentestEngine(target, session)
    await engine.run_phase(phase)
    engine.display_summary()


def interactive_mode():
    print_banner()
    console.print("[bold]Interactive Mode[/bold]\n")

    while True:
        console.print("\n[bold cyan]Commands:[/bold cyan]")
        console.print("  1. New scan        - Start a new pentest")
        console.print("  2. Continue scan   - Resume a previous session")
        console.print("  3. List sessions   - View all sessions")
        console.print("  4. Single phase    - Run a specific phase")
        console.print("  5. Report only     - Generate report from session")
        console.print("  6. Export GitHub   - Export to GitHub")
        console.print("  0. Exit\n")

        choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5", "6"])

        if choice == "0":
            console.print("[dim]Goodbye![/dim]")
            break
        elif choice == "1":
            target = Prompt.ask("Target (domain or URL)")
            asyncio.run(run_full_scan(target))
        elif choice == "2":
            session_id = Prompt.ask("Session ID")
            sessions = Session.list_sessions()
            found = [s for s in sessions if s["session_id"] == session_id]
            if found:
                asyncio.run(run_full_scan(found[0]["target"], session_id))
            else:
                console.print("[red]Session not found[/red]")
        elif choice == "3":
            list_sessions()
        elif choice == "4":
            target = Prompt.ask("Target")
            phase = Prompt.ask("Phase", choices=["recon", "scan", "exploit", "report"])
            asyncio.run(run_phase(target, phase))
        elif choice == "5":
            session_id = Prompt.ask("Session ID")
            try:
                session = Session.load(session_id)
                engine = PentestEngine(session.target, session)
                engine.generate_report()
            except FileNotFoundError:
                console.print("[red]Session not found[/red]")
        elif choice == "6":
            session_id = Prompt.ask("Session ID")
            try:
                session = Session.load(session_id)
                engine = PentestEngine(session.target, session)
                engine.export_to_github()
            except FileNotFoundError:
                console.print("[red]Session not found[/red]")


def main():
    parser = argparse.ArgumentParser(description="PentFlow - Automated Bug Bounty Framework")
    parser.add_argument("target", nargs="?", help="Target domain or URL")
    parser.add_argument("-p", "--phase", choices=["recon", "scan", "exploit", "report"], help="Run specific phase")
    parser.add_argument("-s", "--session", help="Resume session by ID")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--list", action="store_true", help="List all sessions")
    parser.add_argument("--export", help="Export session to GitHub")
    parser.add_argument("-v", "--version", action="version", version=f"PentFlow {VERSION}")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    elif args.list:
        print_banner()
        list_sessions()
    elif args.export:
        try:
            session = Session.load(args.export)
            engine = PentestEngine(session.target, session)
            engine.export_to_github()
        except FileNotFoundError:
            console.print("[red]Session not found[/red]")
    elif args.target:
        print_banner()
        if args.phase:
            asyncio.run(run_phase(args.target, args.phase, args.session))
        else:
            asyncio.run(run_full_scan(args.target, args.session))
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
