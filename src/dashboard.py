"""Day 6/16 - Monitoring dashboard (matplotlib, no extra install needed).
Shows 6 service-health indicators with units, thresholds, the incident window and deploy marker.
Run:  python3 src/dashboard.py   ->  charts/dashboard.png"""
import os, sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
sys.path.insert(0, os.path.dirname(__file__))
from slo import compute

# metric column, panel title, unit label, warning/critical line (None = no line)
PANELS = [
    ("latency_ms",           "Response latency",  "milliseconds",       1000),
    ("error_rate_percent",   "Error rate",        "% of requests",      5),
    ("cpu_percent",          "CPU usage",         "% of capacity",      85),
    ("memory_percent",       "Memory usage",      "% of capacity",      90),
    ("request_rate_per_min", "Traffic",           "requests per minute", None),
    ("disk_percent",         "Disk usage",        "% of capacity",      90),
]

def build(metrics, events, alerts, out="charts/dashboard.png"):
    fig, axes = plt.subplots(3, 2, figsize=(14, 10), sharex=True)
    start, end = (alerts["breach_start"].min(), alerts["breach_end"].max()) if len(alerts) else (None, None)
    deploys = events[events["event_type"].isin(["deploy", "rollback"])]
    for ax, (col, title, unit, limit) in zip(axes.flat, PANELS):
        ax.plot(metrics["timestamp"], metrics[col], lw=1, color="#0e7c86")
        if limit is not None:
            ax.axhline(limit, color="#c0392b", ls="--", lw=1, label=f"limit {limit}")
        if start is not None:
            ax.axvspan(start, end, color="#f2b134", alpha=0.25, label="incident")
        for _, e in deploys.iterrows():
            ax.axvline(e["timestamp"], color="#555", ls=":", lw=1)
        ax.set_title(title, fontsize=11, loc="left", fontweight="bold")
        ax.set_ylabel(unit, fontsize=9)
        ax.grid(alpha=0.25)
        if limit is not None or start is not None:
            ax.legend(loc="upper left", fontsize=8)
    for ax in axes[-1]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.set_xlabel("Time of day, 20 Nov 2026 (1-minute samples)", fontsize=9)
    s = compute(metrics)
    fig.suptitle(f"College Portal health - 24 h   |   SLI {s['sli_percent']}% vs SLO {s['slo_percent']}%   |   "
                 f"error budget used {s['budget_consumed_percent']}%   |   dotted lines = deploy / rollback",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=110); plt.close(fig)
    return out

if __name__ == "__main__":
    m = pd.read_csv("metrics/metrics.csv", parse_dates=["timestamp"])
    e = pd.read_csv("events/events.csv", parse_dates=["timestamp"])
    a = pd.read_csv("alerts/alerts.csv", parse_dates=["fired_at", "breach_start", "breach_end"]) \
        if os.path.exists("alerts/alerts.csv") else pd.DataFrame()
    print("Saved", build(m, e, a))
