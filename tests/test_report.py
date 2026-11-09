import json

from reconciler.compare import Alert
from reconciler.report import prometheus_text, write_reports

RUN = {
    "finished_at": "2026-11-09 15:00 UTC",
    "finished_at_unix": 1794236400,
    "duration_seconds": 3,
    "daos": ["gtc"],
    "summary": {},
}


def test_prometheus_counts_by_labels():
    alerts = [Alert("gtc", "list_duplicate", "medium", "m"), Alert("gtc", "list_duplicate", "medium", "m")]
    text = prometheus_text(alerts, RUN)
    assert 'anticapture_reconciliation_alerts{dao="gtc",type="list_duplicate",severity="medium"} 2' in text
    assert "anticapture_reconciliation_last_run_timestamp_seconds 1794236400" in text


def test_write_reports_creates_three_files(tmp_path):
    alerts = [Alert("gtc", "governor_not_indexed", "critical", "msg", {"a": "x|y"})]
    paths = write_reports(str(tmp_path), RUN, alerts)
    data = json.loads(open(paths["json"]).read())
    assert data["alerts"][0]["type"] == "governor_not_indexed"
    md = open(paths["md"]).read()
    assert "| critical | gtc | governor_not_indexed |" in md and "x/y" in md
    assert open(paths["prom"]).read().startswith("# HELP")
