"""Write alerts.json, alerts.md and metrics.prom."""

from __future__ import annotations

import json
import os

from .compare import SEVERITY_ORDER, Alert


def write_reports(output_dir: str, run: dict, alerts: list[Alert]) -> dict[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    paths = {
        "json": os.path.join(output_dir, "alerts.json"),
        "md": os.path.join(output_dir, "alerts.md"),
        "prom": os.path.join(output_dir, "metrics.prom"),
    }
    with open(paths["json"], "w") as f:
        json.dump({**run, "alerts": [a.to_dict() for a in alerts]}, f, indent=1, ensure_ascii=False, default=str)
    with open(paths["prom"], "w") as f:
        f.write(prometheus_text(alerts, run))
    with open(paths["md"], "w") as f:
        f.write(markdown(alerts, run))
    return paths


def prometheus_text(alerts: list[Alert], run: dict | None = None) -> str:
    counts: dict[tuple[str, str, str], int] = {}
    for a in alerts:
        k = (a.dao, a.type, a.severity)
        counts[k] = counts.get(k, 0) + 1
    lines = [
        "# HELP anticapture_reconciliation_alerts Reconciler alerts by DAO, type and severity",
        "# TYPE anticapture_reconciliation_alerts gauge",
    ]
    for (dao, typ, sev), n in sorted(counts.items()):
        lines.append(f'anticapture_reconciliation_alerts{{dao="{dao}",type="{typ}",severity="{sev}"}} {n}')
    if run:
        lines += [
            "# HELP anticapture_reconciliation_last_run_timestamp_seconds Unix time of the last finished run",
            "# TYPE anticapture_reconciliation_last_run_timestamp_seconds gauge",
            f"anticapture_reconciliation_last_run_timestamp_seconds {run['finished_at_unix']}",
            "# HELP anticapture_reconciliation_duration_seconds Duration of the last run",
            "# TYPE anticapture_reconciliation_duration_seconds gauge",
            f"anticapture_reconciliation_duration_seconds {run['duration_seconds']}",
        ]
    return "\n".join(lines) + "\n"


def markdown(alerts: list[Alert], run: dict) -> str:
    out = [
        "# Reconciler alerts",
        "",
        f"Run finished at {run['finished_at']}, took {run['duration_seconds']} s. "
        f"DAOs: {', '.join(run['daos'])}. Total: {len(alerts)} alerts.",
        "",
        "| Severity | DAO | Type | Message | Evidence |",
        "|---|---|---|---|---|",
    ]
    for a in sorted(alerts, key=lambda x: (SEVERITY_ORDER[x.severity], x.dao, x.type)):
        ev = json.dumps(a.evidence, ensure_ascii=False, default=str).replace("|", "/")
        out.append(f"| {a.severity} | {a.dao} | {a.type} | {a.message} | `{ev}` |")
    return "\n".join(out) + "\n"
