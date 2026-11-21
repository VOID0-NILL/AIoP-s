"""Day 14 - Build the synthetic, non-sensitive incident data that you give to an AI assistant.
Run after pipeline.py.   Output: reports/ai_input.txt"""
import pandas as pd

tl = pd.read_csv("reports/correlated_timeline.csv")
al = pd.read_csv("alerts/alerts.csv", parse_dates=["fired_at", "breach_start", "breach_end"])
m = pd.read_csv("metrics/metrics.csv", parse_dates=["timestamp"])
start, end = al["breach_start"].min(), al["breach_end"].max()
pre = m[(m["timestamp"] >= start - pd.Timedelta(minutes=30)) & (m["timestamp"] < start)]
dur = m[(m["timestamp"] >= start) & (m["timestamp"] <= end)]

L = ["INCIDENT DATA (synthetic College Portal; no real users or systems)", "",
     f"Breach window: {start} to {end} ({int((end - start).total_seconds() // 60) + 1} minutes)", "",
     "Alerts:"]
for _, a in al.iterrows():
    L.append(f"- {a['alert']} ({a['severity']}) fired at {a['fired_at']}, peak value {a['peak_value']}, routed to {a['route']}")
L += ["", "Metrics (average in the 30 minutes before the breach -> maximum during the breach):"]
for c, unit in (("latency_ms", "ms"), ("error_rate_percent", "%"), ("cpu_percent", "%"), ("memory_percent", "%")):
    L.append(f"- {c}: {pre[c].mean():.1f} {unit} -> {dur[c].max():.1f} {unit}")
L.append(f"- request_rate_per_min: {pre['request_rate_per_min'].mean():.0f} before -> {dur['request_rate_per_min'].mean():.0f} average during")
L += ["", "Timeline (time | source | where | what):"]
for _, r in tl.iterrows():
    L.append(f"- {r['time']} | {r['source']} | {r['where']} | {r['what']}")
open("reports/ai_input.txt", "w").write("\n".join(L))
print("\n".join(L)); print("\nSaved reports/ai_input.txt")
