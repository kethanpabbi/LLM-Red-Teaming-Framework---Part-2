"""
Garak integration — runs automated vulnerability probes against a model.
Uses --target_type and --target_name flags (garak v0.14+).

Usage:
  python3 tools/garak_runner.py --model tinyllama
  python3 tools/garak_runner.py --model phi3
"""

import subprocess
import json
import os
import argparse
from datetime import datetime
from rich.console import Console

console = Console()

GARAK_PROBES = [
    "promptinject",
    "dan",
    "encoding",
    "continuation",
]

MODEL_CONFIG = {
    "tinyllama": {"target_type": "ollama", "target_name": "tinyllama"},
    "phi3":      {"target_type": "ollama", "target_name": "phi3:mini"},
}


def run_garak_scan(model: str, output_dir: str = "results/garak") -> str:
    os.makedirs(output_dir, exist_ok=True)

    if model not in MODEL_CONFIG:
        raise ValueError(f"Unknown model: {model}. Use 'tinyllama' or 'phi3'.")

    config = MODEL_CONFIG[model]
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report_prefix = os.path.join(os.getcwd(), output_dir, f"garak_{model}_{timestamp}")
    probes_arg = ",".join(GARAK_PROBES)

    console.print(f"\n[bold red]🔍 Running Garak on {model}...[/bold red]")
    console.print(f"[dim]Probes      : {probes_arg}[/dim]")
    console.print(f"[dim]Target type : {config['target_type']}[/dim]")
    console.print(f"[dim]Target name : {config['target_name']}[/dim]\n")

    cmd = [
        "python3", "-m", "garak",
        "--target_type", config["target_type"],
        "--target_name", config["target_name"],
        "--probes", probes_arg,
        "--report_prefix", report_prefix,
        "--skip_unknown",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.stdout:
            console.print(result.stdout)
        if result.returncode != 0 and result.stderr:
            console.print(f"[yellow]Garak stderr:[/yellow]\n{result.stderr[:800]}")
    except subprocess.TimeoutExpired:
        console.print("[red]Garak timed out after 10 minutes[/red]")
    except Exception as e:
        console.print(f"[red]Garak error: {e}[/red]")

    # Find generated .jsonl report
    for f in sorted(os.listdir(output_dir), reverse=True):
        if f.startswith(f"garak_{model}_{timestamp}") and f.endswith(".jsonl"):
            return os.path.join(output_dir, f)

    return report_prefix + ".jsonl"


def parse_garak_results(report_path: str) -> dict:
    if not os.path.exists(report_path):
        return {"error": f"Report not found: {report_path}"}

    results = {"total": 0, "passed": 0, "failed": 0, "probes": {}}

    with open(report_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                probe = entry.get("probe", "unknown")
                passed = entry.get("passed", False)
                results["total"] += 1
                if passed:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                if probe not in results["probes"]:
                    results["probes"][probe] = {"total": 0, "failed": 0}
                results["probes"][probe]["total"] += 1
                if not passed:
                    results["probes"][probe]["failed"] += 1
            except json.JSONDecodeError:
                continue

    if results["total"] > 0:
        results["pass_rate"] = round(results["passed"] / results["total"] * 100, 1)
        results["fail_rate"] = round(results["failed"] / results["total"] * 100, 1)

    return results


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=["tinyllama", "phi3"])
    args = parser.parse_args()

    report_path = run_garak_scan(args.model)
    console.print(f"\n[green]Garak report: {report_path}[/green]")

    results = parse_garak_results(report_path)
    console.print(f"\n[bold]Garak Summary:[/bold]")
    console.print(f"  Total  : {results.get('total', 0)}")
    console.print(f"  Passed : {results.get('passed', 0)}")
    console.print(f"  Failed : {results.get('failed', 0)}")
    console.print(f"  Rate   : {results.get('pass_rate', 'N/A')}%")