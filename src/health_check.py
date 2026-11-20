"""Day 12 - Safe, read-only health check on a metrics CSV.
Exit codes: 0 = OK, 1 = WARNING, 2 = CRITICAL, 3 = could not run (bad input)."""
import argparse, logging, sys
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
    log.info("Result: %s", ["OK", "WARNING", "CRITICAL"][code])
    return code

if __name__ == "__main__":
    sys.exit(main())
