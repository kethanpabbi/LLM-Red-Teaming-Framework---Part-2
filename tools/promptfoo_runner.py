"""
PromptFoo integration — runs YAML-defined test suite and parses results.

Usage:
  python3 tools/promptfoo_runner.py
"""

import subprocess
import json
import os
from rich.console import Console
from rich.table import Table

console = Console()


def run_promptfoo(config_path: str = "config/promptfooconfig.yaml") -> dict:
    console.print(f"\n[bold yellow]⚡ Running PromptFoo eval...[/bold yellow]")
    console.print(f"[dim]Config: {config_path}[/dim]\n")

    cmd = ["promptfoo", "eval", "--config", config_path, "--output", "results/promptfoo_results.json"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            console.print(f"[yellow]PromptFoo output:[/yellow]\n{result.stdout[:1000]}")
            console.print(f"[red]PromptFoo stderr:[/red]\n{result.stderr[:500]}")
        else:
            console.print(result.stdout)
    except subprocess.TimeoutExpired:
        console.print("[red]PromptFoo timed out[/red]")
    except FileNotFoundError:
        console.print("[red]promptfoo not found — run: npm install -g promptfoo[/red]")
        return {}

    return parse_promptfoo_results("results/promptfoo_results.json")


def parse_promptfoo_results(results_path: str) -> dict:
    if not os.path.exists(results_path):
        return {"error": "Results file not found"}

    with open(results_path) as f:
        data = json.load(f)

    summary = {"providers": {}, "total_tests": 0, "overall_pass": 0, "overall_fail": 0}

    results = data.get("results", {}).get("results", [])
    for r in results:
        provider = r.get("provider", {}).get("label", "unknown")
        passed = r.get("success", False)

        if provider not in summary["providers"]:
            summary["providers"][provider] = {"pass": 0, "fail": 0, "tests": []}

        if passed:
            summary["providers"][provider]["pass"] += 1
            summary["overall_pass"] += 1
        else:
            summary["providers"][provider]["fail"] += 1
            summary["overall_fail"] += 1

        summary["total_tests"] += 1
        summary["providers"][provider]["tests"].append({
            "description": r.get("description", ""),
            "passed": passed,
            "prompt": r.get("prompt", {}).get("raw", "")[:100],
        })

    for provider, stats in summary["providers"].items():
        total = stats["pass"] + stats["fail"]
        stats["pass_rate"] = round(stats["pass"] / total * 100, 1) if total > 0 else 0

    return summary


def print_promptfoo_summary(summary: dict):
    if "error" in summary:
        console.print(f"[red]{summary['error']}[/red]")
        return

    table = Table(title="PromptFoo Results by Model")
    table.add_column("Model", style="cyan")
    table.add_column("Passed", style="green")
    table.add_column("Failed", style="red")
    table.add_column("Pass Rate", style="yellow")

    for provider, stats in summary["providers"].items():
        table.add_row(provider, str(stats["pass"]), str(stats["fail"]), f"{stats['pass_rate']}%")

    console.print(table)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    summary = run_promptfoo()
    print_promptfoo_summary(summary)
