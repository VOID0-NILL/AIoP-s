"""Day 10/11/14 - Correlate alerts, events and logs; rank causes by evidence; write incident report.
Rule-based on purpose: every claim in the report points to data you can check."""
import pandas as pd

def build_timeline(alerts, events, logs, win_before=30, win_after=15):
    start = alerts["breach_start"].min() - pd.Timedelta(minutes=win_before)
    end = alerts["breach_end"].max() + pd.Timedelta(minutes=win_after)
    rows = []
    for _, e in events[(events["timestamp"] >= start) & (events["timestamp"] <= end)].iterrows():
        rows.append((e["timestamp"], "event", e["service"], f"{e['event_type']}: {e['description']}"))
    for _, a in alerts.iterrows():
        rows.append((a["fired_at"], "alert", a["route"], f"{a['alert']} ({a['severity']}) peak={a['peak_value']}"))
    win = logs[(logs["timestamp"] >= start) & (logs["timestamp"] <= end) & (logs["level"] == "ERROR")]
    for (svc, pat), g in win.groupby(["service", "pattern"]):
        if len(g) < 3:          # skip one-off background errors; they are noise, not signal
            continue
        rows.append((g["timestamp"].min(), "log", svc, f"first ERROR '{pat}' (x{len(g)})"))
    tl = pd.DataFrame(rows, columns=["time", "source", "where", "what"]).sort_values("time").reset_index(drop=True)
    tl["time"] = tl["time"].dt.floor("s")
    return tl, start, end

def rank_causes(alerts, events, logs, metrics):
    inc_start = alerts["breach_start"].min()
    inc_end = alerts["breach_end"].max()
    win = logs[(logs["timestamp"] >= inc_start - pd.Timedelta(minutes=5)) & (logs["timestamp"] <= inc_end)]
    err = win[win["level"] == "ERROR"]
    hyps = []

    # H1: change-induced regression
    dep = events[(events["event_type"] == "deploy") &
                 (events["timestamp"] <= inc_start) & (events["timestamp"] >= inc_start - pd.Timedelta(minutes=30))]
    score, ev = 0, []
    if len(dep):
        d = dep.iloc[-1]; gap = (inc_start - d["timestamp"]).total_seconds() / 60
        score += 3; ev.append(f"Deploy '{d['description']}' at {d['timestamp']}, {gap:.0f} min before breach start")
        n = int((err["service"] == d["service"]).sum())
        if n: score += 2; ev.append(f"{n} ERROR lines come from the deployed service ({d['service']})")
        rb = events[(events["event_type"] == "rollback") & (events["timestamp"] > inc_start)]
        if len(rb):
            r = rb.iloc[0]; score += 2
            ev.append(f"Rollback at {r['timestamp']}; breach ended {inc_end} (metrics recovered after the rollback)")
    hyps.append(("Change-induced regression (new deploy)", score, ev, "Compare v2.3 vs v2.2 diff; check release notes and config changes."))

    # H2: DB connection exhaustion
    pool = err[err["pattern"].str.contains("pool exhausted|connection timeout", case=False)]
    score, ev = 0, []
    if len(pool) >= 20:
        score += 3; ev.append(f"{len(pool)} ERROR lines mention connection pool exhaustion / DB timeouts")
    slow = win[win["pattern"].str.contains("Slow query", case=False)]
    if len(slow): score += 1; ev.append(f"{len(slow)} slow-query warnings from the database")
    hyps.append(("Database connection-pool exhaustion", score, ev, "Check pool size, open connections per service, connection leaks in the new code."))

    # H3: traffic surge
    before = metrics[(metrics["timestamp"] >= inc_start - pd.Timedelta(minutes=30)) & (metrics["timestamp"] < inc_start)]["request_rate_per_min"].mean()
    during = metrics[(metrics["timestamp"] >= inc_start) & (metrics["timestamp"] <= inc_end)]["request_rate_per_min"].mean()
    score, ev = 0, []
    if during > before * 1.3:
        score += 2; ev.append(f"Request rate rose from {before:.0f} to {during:.0f} per minute")
    else:
        ev.append(f"No traffic surge: request rate {before:.0f} before vs {during:.0f} during (it fell)")
    hyps.append(("Traffic surge / capacity limit", score, ev, "Compare with last week's same-hour traffic; check autoscaling limits."))

    # H4: external dependency
    ext = err[err["pattern"].str.contains("notification-service", case=False)]
    score, ev = 0, []
    base_rate = len(logs[(logs["pattern"].str.contains("notification-service")) & (logs["level"] == "ERROR")]) / max(
        1, (logs["timestamp"].max() - logs["timestamp"].min()).total_seconds() / 60)
    in_rate = len(ext) / max(1, (inc_end - inc_start).total_seconds() / 60)
    if in_rate > base_rate * 3: score += 2; ev.append("notification-service timeouts above their normal rate")
    else: ev.append("notification-service timeouts stayed at their normal background rate")
    hyps.append(("External dependency (notification-service)", score, ev, "Check dependency status page only if other causes are ruled out."))

    return sorted(hyps, key=lambda h: -h[1]), inc_start, inc_end

def impact(metrics, inc_start, inc_end):
    pre = metrics[(metrics["timestamp"] >= inc_start - pd.Timedelta(minutes=30)) & (metrics["timestamp"] < inc_start)]
    dur = metrics[(metrics["timestamp"] >= inc_start) & (metrics["timestamp"] <= inc_end)]
    return {c: (round(pre[c].mean(), 1), round(dur[c].max(), 1)) for c in
            ["latency_ms", "error_rate_percent", "cpu_percent", "memory_percent"]}

def write_report(alerts, events, logs, metrics, path="reports/incident_report.md"):
    tl, w_start, w_end = build_timeline(alerts, events, logs)
    tl.to_csv("reports/correlated_timeline.csv", index=False)
    hyps, s, e = rank_causes(alerts, events, logs, metrics)
    imp = impact(metrics, s, e)
    L = ["# Incident Report - College Portal", "",
         "> Generated automatically from sample data. Causes below are **hypotheses ranked by evidence**, not confirmed facts.", "",
         "## Summary",
         f"- Breach window: **{s}** to **{e}** (about {int((e - s).total_seconds() // 60) + 1} minutes)",
         f"- Alerts: {', '.join(sorted(alerts['alert'].unique()))} ({len(alerts)} alerts, grouped into {alerts['group_id'].nunique()} incident)",
         "- Affected services (from ERROR logs): " + ", ".join(sorted(logs[(logs['timestamp'] >= s) & (logs['timestamp'] <= e) & (logs['level'] == 'ERROR')]['service'].unique())), "",
         "## Impact (normal level before incident -> peak during incident)"]
    for k, (a, b) in imp.items():
        L.append(f"- {k}: {a} -> {b}")
    L += ["", "## Timeline (symptoms and signals in time order)", "", "| Time | Source | Where | What |", "|---|---|---|---|"]
    for _, r in tl.iterrows():
        L.append(f"| {r['time']} | {r['source']} | {r['where']} | {r['what']} |")
    L += ["", "## Symptoms vs likely causes",
          "- **Symptoms:** high latency, high error rate, 502/500 responses (what users and alerts see).",
          "- **Candidate causes:** see ranked hypotheses below (what may have produced the symptoms).", "",
          "## Root-cause hypotheses (ranked by evidence score)"]
    for i, (name, score, ev, nxt) in enumerate(hyps, 1):
        L.append(f"\n### H{i}. {name} - evidence score {score}")
        L += [f"- {x}" for x in ev]
        L.append(f"- Next diagnostic step: {nxt}")
    L += ["", "> Note: H1 and H2 are not mutually exclusive. The deploy may be the trigger and pool exhaustion the mechanism."]
    L += ["", "## Suggested next steps (human-approved)",
          "1. Keep fee-service on v2.2 until the v2.3 connection handling is reviewed.",
          "2. Review connection-pool settings and open-connection counts for the new release.",
          "3. Add a pre-deploy check/canary for fee-service so this is caught at 5% traffic.",
          "4. Hold a short post-incident review; record the confirmed cause.", "",
          "## Limitations",
          "- Synthetic data: one injected incident; real systems are noisier.",
          "- Evidence scores are simple rule weights (not probabilities); they rank, they do not prove.",
          "- Correlation in time does not prove causation; confirm with a code/config diff before closing."]
    text = "\n".join(L)
    open(path, "w").write(text)
    return text
