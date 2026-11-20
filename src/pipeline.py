"""Day 18/20 - End-to-end AIOps pipeline:
ingest -> parse -> detect anomalies -> alert -> correlate -> incident report."""
import os, sys, time
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from parse_logs import parse_file, summarise
from detect_anomalies import detect, evaluate, plot
from alerts import evaluate_rules, group_alerts
from incident_report import write_report

def step(name, fn):
    t = time.time(); out = fn(); print(f"[{time.time() - t:5.2f}s] {name}"); return out

def run():
    for d in ("reports", "charts", "alerts"): os.makedirs(d, exist_ok=True)
    logs, bad = step("1. Parse logs", lambda: parse_file("logs/portal.log"))
    metrics = step("2. Load metrics", lambda: pd.read_csv("metrics/metrics.csv", parse_dates=["timestamp"]))
    events = step("3. Load events", lambda: pd.read_csv("events/events.csv", parse_dates=["timestamp"]))
    open("reports/log_findings.md", "w").write(summarise(logs, bad))
    det = step("4. Detect anomalies", lambda: detect(metrics))
    plot(det)
    res = None
    if os.path.exists("labels/incident_labels.csv"):
        res = evaluate(det, pd.read_csv("labels/incident_labels.csv"))
        print("    detection vs ground truth:", res)
    alerts = step("5. Evaluate alert rules", lambda: group_alerts(evaluate_rules(metrics)))
    alerts.to_csv("alerts/alerts.csv", index=False)
    print(f"    {len(alerts)} alert(s) in {alerts['group_id'].nunique() if len(alerts) else 0} group(s)")
    if alerts.empty:
        print("No alerts fired - no incident report needed."); return
    step("6. Correlate + incident report", lambda: write_report(alerts, events, logs, metrics))
    print("\nDone. See reports/incident_report.md, reports/correlated_timeline.csv, charts/anomalies.png")

if __name__ == "__main__":
    run()
