"""Command-line entry point: ``python -m reconciler``."""

from __future__ import annotations

import argparse
import sys
import time

from .chain import Chain
from .checks import Checker, fmt_ts
from .config import DAOS, Settings, load_dotenv
from .http import ApiClient, RpcClient
from .lists import load_constants, parse_lists
from .report import write_reports


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m reconciler",
        description="Compare the public Anticapture API with on-chain data (read-only).",
    )
    p.add_argument(
        "--daos", default=",".join(DAOS), help=f"comma-separated DAO ids (default: all). Known: {', '.join(DAOS)}"
    )
    p.add_argument("--output", default="output", help="directory for alerts.json, alerts.md, metrics.prom")
    p.add_argument(
        "--fail-on",
        choices=["never", "critical", "high"],
        default="never",
        help="exit with code 2 if an alert of this severity or worse is found",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    args = build_parser().parse_args(argv)
    daos = [d.strip() for d in args.daos.split(",") if d.strip()]
    unknown = [d for d in daos if d not in DAOS]
    if unknown:
        print(f"unknown DAO id(s): {', '.join(unknown)}. Known: {', '.join(DAOS)}", file=sys.stderr)
        return 1

    settings = Settings.from_env()
    source = load_constants(settings.constants_path, settings.constants_url, settings.http_timeout_s)
    lists, commented = parse_lists(source)
    checker = Checker(
        settings,
        ApiClient(settings.api_url, settings.api_min_interval_s, settings.http_timeout_s),
        Chain(RpcClient(settings.rpc_urls, settings.http_timeout_s)),
        lists,
        commented,
    )

    started = time.time()
    summary = {}
    for dao in daos:
        summary[dao] = checker.run_dao(dao, DAOS[dao])
        print(f"{dao}: done", flush=True)
    finished = int(time.time())
    run = {
        "finished_at": fmt_ts(finished),
        "finished_at_unix": finished,
        "duration_seconds": round(time.time() - started),
        "daos": daos,
        "api_url": settings.api_url,
        "constants_source": settings.constants_path or settings.constants_url,
        "summary": summary,
    }
    paths = write_reports(args.output, run, checker.alerts)
    print(f"{len(checker.alerts)} alerts -> {paths['md']}")

    if args.fail_on != "never":
        limit = {"critical": 0, "high": 1}[args.fail_on]
        from .compare import SEVERITY_ORDER

        if any(SEVERITY_ORDER[a.severity] <= limit for a in checker.alerts):
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
