"""
Side-by-side model comparison — runs same attacks against both models
and generates a comparison table + report.
"""

import sqlite3
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table

console = Console()
DB_PATH = os.getenv("RESULTS_DB", "results/red_team_results.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT UNIQUE NOT NULL,
            model TEXT NOT NULL,
            provider TEXT NOT NULL,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            total_attacks INTEGER DEFAULT 0,
            successful_attacks INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            attack_name TEXT NOT NULL,
            category TEXT NOT NULL,
            payload TEXT NOT NULL,
            response TEXT,
            success INTEGER NOT NULL DEFAULT 0,
            severity TEXT NOT NULL DEFAULT 'low',
            reason TEXT,
            timestamp TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()


def save_run(run_id, model, provider):
    conn = get_connection()
    conn.execute("INSERT OR IGNORE INTO runs (run_id, model, provider, started_at) VALUES (?, ?, ?, ?)",
                 (run_id, model, provider, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def save_result(run_id, attack_name, category, payload, response, success, severity, reason):
    conn = get_connection()
    conn.execute("""INSERT INTO results (run_id, attack_name, category, payload, response, success, severity, reason, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                 (run_id, attack_name, category, payload, response,
                  int(success), severity, reason, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def finalize_run(run_id):
    conn = get_connection()
    conn.execute("""UPDATE runs SET finished_at=?,
                    total_attacks=(SELECT COUNT(*) FROM results WHERE run_id=?),
                    successful_attacks=(SELECT COUNT(*) FROM results WHERE run_id=? AND success=1)
                    WHERE run_id=?""",
                 (datetime.utcnow().isoformat(), run_id, run_id, run_id))
    conn.commit()
    conn.close()


def get_run_results(run_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM results WHERE run_id=? ORDER BY timestamp", (run_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_run_summary(run_id):
    conn = get_connection()
    run = conn.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
    conn.close()
    return dict(run) if run else {}


def compare_runs(run_id_1: str, run_id_2: str):
    """Print a side-by-side comparison of two runs."""
    s1 = get_run_summary(run_id_1)
    s2 = get_run_summary(run_id_2)
    r1 = get_run_results(run_id_1)
    r2 = get_run_results(run_id_2)

    def stats(results):
        total = len(results)
        vulns = [r for r in results if r["success"]]
        sev = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for r in vulns:
            sev[r["severity"]] = sev.get(r["severity"], 0) + 1
        rate = round(len(vulns) / total * 100, 1) if total else 0
        return total, len(vulns), rate, sev

    t1, v1, rate1, sev1 = stats(r1)
    t2, v2, rate2, sev2 = stats(r2)

    table = Table(title="Model Comparison")
    table.add_column("Metric", style="cyan")
    table.add_column(f"{s1.get('model', run_id_1)}", style="red")
    table.add_column(f"{s2.get('model', run_id_2)}", style="green")

    table.add_row("Total Attacks", str(t1), str(t2))
    table.add_row("Vulnerabilities Found", str(v1), str(v2))
    table.add_row("Attack Success Rate", f"{rate1}%", f"{rate2}%")
    table.add_row("Critical", str(sev1["critical"]), str(sev2["critical"]))
    table.add_row("High", str(sev1["high"]), str(sev2["high"]))
    table.add_row("Medium", str(sev1["medium"]), str(sev2["medium"]))

    console.print(f"\n[bold]{'='*60}[/bold]")
    console.print(table)

    return {"model1": {"run_id": run_id_1, **s1, "vulns": v1, "rate": rate1, "severity": sev1},
            "model2": {"run_id": run_id_2, **s2, "vulns": v2, "rate": rate2, "severity": sev2}}
