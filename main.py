#!/usr/bin/env python3
"""
LLM Red Team Framework — Part 2: Open Source Models

Usage:
  python3 main.py --model gpt2
  python3 main.py --model phi3
  python3 main.py --compare --run1 run_abc123 --run2 run_def456
"""

import argparse
import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import track

load_dotenv()
console = Console()


def run_scan(model: str):
    from clients import get_client
    from attacks import ALL_ATTACK_CLASSES
    from evaluation.comparator import init_db, save_run, save_result, finalize_run

    init_db()
    run_id = f"run_{model}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    client = get_client(model)
    save_run(run_id, client.model, client.provider_name())

    console.print(f"\n[bold red]🔴 LLM Red Team — Part 2[/bold red]")
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
    rate = f"{len(vulns)/total*100:.1f}%" if total > 0 else "N/A (all errored)"
    console.print(f"\n[bold]Scan complete — {len(vulns)}/{total} attacks succeeded ({rate})[/bold]")
    console.print(f"[dim]Run ID: {run_id}[/dim]\n")    
    return run_id


def main():
    parser = argparse.ArgumentParser(description="LLM Red Team Framework Part 2")
    parser.add_argument("--model", choices=["gpt2", "phi3"], help="Model to test")
    parser.add_argument("--compare", action="store_true", help="Compare two existing runs")
    parser.add_argument("--run1", help="First run ID for comparison")
    parser.add_argument("--run2", help="Second run ID for comparison")
    parser.add_argument("--garak", action="store_true", help="Run Garak scan")
    parser.add_argument("--promptfoo", action="store_true", help="Run PromptFoo eval")
    args = parser.parse_args()

    if args.garak and args.model:
        from tools.garak_runner import run_garak_scan
        run_garak_scan(args.model)

    elif args.promptfoo:
        from tools.promptfoo_runner import run_promptfoo, print_promptfoo_summary
        summary = run_promptfoo()
        print_promptfoo_summary(summary)

    elif args.compare and args.run1 and args.run2:
        from evaluation.comparator import compare_runs
        compare_runs(args.run1, args.run2)

    elif args.model:
        if args.model == "gpt2" and not os.getenv("HF_API_TOKEN"):
            console.print("[red]Error: HF_API_TOKEN not set in .env[/red]")
            sys.exit(1)
        run_scan(args.model)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
