"""Day 12 - Safe, read-only health check on a metrics CSV.
Exit codes: 0 = OK, 1 = WARNING, 2 = CRITICAL, 3 = could not run (bad input)."""
import argparse, logging, os, sys
from datetime import datetime
import pandas as pd

THRESHOLDS = {  # metric: (warning, critical)
    "cpu_percent": (70, 85), "memory_percent": (80, 90), "disk_percent": (80, 90),
    "latency_ms": (500, 1000), "error_rate_percent": (2, 5),
}
log = logging.getLogger("health_check")

def check_row(row, thresholds=THRESHOLDS):
    """Return (worst_exit_code, list of findings) for one metrics row."""
    worst, findings = 0, []
    for metric, (warn, crit) in thresholds.items():
        v = row.get(metric)
        if v is None or pd.isna(v):
            findings.append(f"{metric}: MISSING"); worst = max(worst, 1); continue
        if v >= crit: findings.append(f"{metric}={v} CRITICAL (>= {crit})"); worst = max(worst, 2)
        elif v >= warn: findings.append(f"{metric}={v} WARNING (>= {warn})"); worst = max(worst, 1)
        else: findings.append(f"{metric}={v} OK")
    return worst, findings

def main(argv=None):
    p = argparse.ArgumentParser(description="Read-only health check on a metrics CSV")
    p.add_argument("--metrics", default="metrics/metrics.csv")
    p.add_argument("--at", help="timestamp to check, e.g. '2026-11-20 14:20:00' (default: last row)")
    p.add_argument("--report", action="store_true", help="also write a timestamped report file in reports/")
    a = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        df = pd.read_csv(a.metrics, parse_dates=["timestamp"])
        row = df[df["timestamp"] == pd.to_datetime(a.at)].iloc[0] if a.at else df.iloc[-1]
    except (FileNotFoundError, IndexError, KeyError, ValueError, pd.errors.ParserError) as exc:
        log.error("Cannot run check: %s", exc); return 3
    code, findings = check_row(row.to_dict())
    log.info("Checked %s", row["timestamp"])
    for f in findings: log.info(f)
    result = ["OK", "WARNING", "CRITICAL"][code]
    log.info("Result: %s", result)
    if a.report:
        try:
            os.makedirs("reports", exist_ok=True)
            path = f"reports/health_report_{datetime.now():%Y%m%d_%H%M%S}.txt"
            with open(path, "w") as f:
                f.write(f"Health report generated {datetime.now():%Y-%m-%d %H:%M:%S}\n")
                f.write(f"Input file: {a.metrics}\nChecked sample time: {row['timestamp']}\n\n")
                f.write("\n".join(findings) + f"\n\nResult: {result} (exit code {code})\n")
            log.info("Report written: %s", path)
        except OSError as exc:
            log.error("Could not write report: %s", exc); return 3
    return code

if __name__ == "__main__":
    sys.exit(main())
