"""
Garak integration — runs automated vulnerability probes against a model.

Garak probes used:
  - promptinject   : Prompt injection attacks
  - dan            : DAN-style jailbreaks
  - encoding       : Base64/ROT13 encoded attacks
  - knownbadsignatures : Known attack signatures
  - malwaregen     : Malware generation attempts
  - continuation   : Harmful content continuation

Usage:
  python3 tools/garak_runner.py --model gpt2
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
    "knownbadsignatures",
    "continuation",
]

MODEL_CONFIG = {
    "gpt2": {
        "model_type": "huggingface.InferenceAPI",
        "model_name": "gpt2",
    },
    "phi3": {
        "model_type": "ollama",
        "model_name": "phi3:mini",
    },
}


def run_garak_scan(model: str, output_dir: str = "results/garak") -> str:
    os.makedirs(output_dir, exist_ok=True)

    if model not in MODEL_CONFIG:
        raise ValueError(f"Unknown model: {model}. Use 'gpt2' or 'phi3'.")

    config = MODEL_CONFIG[model]
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(output_dir, f"garak_{model}_{timestamp}.json")
    probes_arg = ",".join(GARAK_PROBES)

    console.print(f"\n[bold red]🔍 Running Garak on {model}...[/bold red]")
    console.print(f"[dim]Probes: {probes_arg}[/dim]")
    console.print(f"[dim]Model type: {config['model_type']}[/dim]\n")

    cmd = [
        "python3", "-m", "garak",
        "--model_type", config["model_type"],
        "--model_name", config["model_name"],
        "--probes", probes_arg,
        "--report_prefix", report_file.replace(".json", ""),
    ]

    # Add HF token for HuggingFace models
    env = os.environ.copy()
    if model == "gpt2":
        hf_token = os.getenv("HF_API_TOKEN", "")
        if hf_token:
            env["HF_INFERENCE_TOKEN"] = hf_token

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=300)
        console.print(result.stdout)
        if result.returncode != 0:
            console.print(f"[yellow]Garak stderr:[/yellow] {result.stderr[:500]}")
    except subprocess.TimeoutExpired:
        console.print("[red]Garak scan timed out after 5 minutes[/red]")
    except Exception as e:
        console.print(f"[red]Garak error: {e}[/red]")

    # Find the generated report
    for f in os.listdir(output_dir):
        if f.startswith(f"garak_{model}_{timestamp}") and f.endswith(".jsonl"):
            return os.path.join(output_dir, f)

    return report_file


def parse_garak_results(report_path: str) -> dict:
    """Parse Garak JSONL output into a summary dict."""
    if not os.path.exists(report_path):
        return {"error": f"Report not found: {report_path}"}

    results = {"total": 0, "passed": 0, "failed": 0, "probes": {}}

    with open(report_path) as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
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
    parser.add_argument("--model", required=True, choices=["gpt2", "phi3"])
    args = parser.parse_args()

    report_path = run_garak_scan(args.model)
    console.print(f"\n[green]Garak report: {report_path}[/green]")

    results = parse_garak_results(report_path)
    console.print(f"\n[bold]Garak Summary:[/bold]")
    console.print(f"  Total probes : {results.get('total', 0)}")
    console.print(f"  Passed       : {results.get('passed', 0)}")
    console.print(f"  Failed       : {results.get('failed', 0)}")
    console.print(f"  Pass rate    : {results.get('pass_rate', 0)}%")
