#!/usr/bin/env python3
"""
LLM Red Teaming Framework — Part 2: Open Source Models

Usage:
  # Run individual tools
  python3 main.py --model tinyllama                          # custom attacks only
  python3 main.py --model tinyllama --garak                  # garak only
  python3 main.py --model tinyllama --promptfoo              # promptfoo only

  # Run everything at once
  python3 main.py --model tinyllama --full                   # all three tools
  python3 main.py --model phi3 --full

  # Compare two runs
  python3 main.py --compare --run1 run_tinyllama_xxx --run2 run_phi3_xxx
"""

import argparse
import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import track
from rich.rule import Rule

load_dotenv()
console = Console()


def run_custom_scan(model: str) -> str:
    from clients import get_client
    from attacks import ALL_ATTACK_CLASSES
    from evaluation.comparator import init_db, save_run, save_result, finalize_run

    init_db()
    run_id = f"run_{model}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    client = get_client(model)
    save_run(run_id, client.model, client.provider_name())

    console.print(Rule("[bold red]Custom Attack Suite[/bold red]"))
    console.print(f"[dim]Run ID  : {run_id}[/dim]")
    console.print(f"[dim]Model   : {client.model} ({client.provider_name()})[/dim]")
    console.print(f"[dim]Started : {datetime.utcnow().isoformat()}[/dim]\n")

    all_results = []
    for AttackClass in ALL_ATTACK_CLASSES:
        instance = AttackClass(client=client)
        console.print(f"[yellow]▶ {AttackClass.__name__}[/yellow]")
        for attack_name, payload in track(instance.get_payloads(), description=f"  {instance.category}"):
            try:
                result = instance.run(payload, attack_name)
                all_results.append(result)
                save_result(run_id, result.attack_name, result.category, result.payload,
                            result.response, result.success, result.severity, result.reason)
                status = "[red]✗ VULN[/red]" if result.success else "[green]✓ SAFE[/green]"
                console.print(f"    {attack_name}: {status} [{result.severity.upper()}]")
            except Exception as e:
                console.print(f"    [dim]{attack_name}: ERROR — {e}[/dim]")

    finalize_run(run_id)
    total = len(all_results)
    vulns = [r for r in all_results if r.success]
    rate = f"{len(vulns)/total*100:.1f}%" if total > 0 else "N/A"
    console.print(f"\n[bold]✅ Custom scan done — {len(vulns)}/{total} vulnerabilities ({rate})[/bold]")
    console.print(f"[dim]Run ID: {run_id}[/dim]\n")
    return run_id


def run_garak_scan(model: str):
    from tools.garak_runner import run_garak_scan as _garak, parse_garak_results
    console.print(Rule("[bold red]Garak Vulnerability Scanner[/bold red]"))
    report_path = _garak(model)
    results = parse_garak_results(report_path)
    console.print(f"\n[bold]✅ Garak done[/bold]")
    console.print(f"  Pass rate : {results.get('pass_rate', 'N/A')}%")
    console.print(f"  Failed    : {results.get('failed', 'N/A')}/{results.get('total', 'N/A')} probes\n")


def run_promptfoo_scan():
    from tools.promptfoo_runner import run_promptfoo, print_promptfoo_summary
    console.print(Rule("[bold red]PromptFoo Test Harness[/bold red]"))
    summary = run_promptfoo()
    print_promptfoo_summary(summary)
    console.print(f"\n[bold]✅ PromptFoo done[/bold]\n")


def main():
    parser = argparse.ArgumentParser(description="LLM Red Teaming Framework Part 2")
    parser.add_argument("--model", choices=["tinyllama", "phi3"], help="Model to test")
    parser.add_argument("--full", action="store_true", help="Run all tools: custom + garak + promptfoo")
    parser.add_argument("--garak", action="store_true", help="Run Garak scan only")
    parser.add_argument("--promptfoo", action="store_true", help="Run PromptFoo eval only")
    parser.add_argument("--compare", action="store_true", help="Compare two existing runs")
    parser.add_argument("--run1", help="First run ID for comparison")
    parser.add_argument("--run2", help="Second run ID for comparison")
    args = parser.parse_args()

    # ── Compare mode ──────────────────────────────────────────
    if args.compare:
        if not args.run1 or not args.run2:
            console.print("[red]--compare requires --run1 and --run2[/red]")
            sys.exit(1)
        from evaluation.comparator import compare_runs
        compare_runs(args.run1, args.run2)
        return

    # ── Require --model for everything else ───────────────────
    if not args.model:
        parser.print_help()
        sys.exit(1)

    # ── Run all three tools ───────────────────────────────────
    if args.full:
        console.print(f"\n[bold red]🔴 LLM Red Team — FULL SCAN: {args.model}[/bold red]\n")
        run_id = run_custom_scan(args.model)
        run_garak_scan(args.model)
        run_promptfoo_scan()
        console.print(Rule("[bold green]All scans complete[/bold green]"))
        console.print(f"[dim]Custom scan run ID: {run_id}[/dim]")
        console.print(f"[dim]Garak report      : results/garak/[/dim]")
        console.print(f"[dim]PromptFoo report  : results/promptfoo_results.json[/dim]\n")
        return

    # ── Individual tools ──────────────────────────────────────
    if args.garak:
        run_garak_scan(args.model)
    elif args.promptfoo:
        run_promptfoo_scan()
    else:
        # default: custom attacks only
        console.print(f"\n[bold red]🔴 LLM Red Team — Part 2[/bold red]\n")
        run_custom_scan(args.model)


if __name__ == "__main__":
    main()
