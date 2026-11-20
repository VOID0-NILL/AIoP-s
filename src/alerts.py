"""Day 9 - Rule-based alerts with duration, severity, routing and de-duplication."""
import pandas as pd

RULES = [
    # name, metric, op, threshold, for_minutes, severity, route
    ("HighLatency",   "latency_ms",         ">", 800, 3, "critical", "oncall-app-team"),
    ("HighErrorRate", "error_rate_percent", ">", 5,   3, "critical", "oncall-app-team"),
    ("HighCPU",       "cpu_percent",        ">", 85,  5, "warning",  "infra-team"),
    ("DiskAlmostFull","disk_percent",       ">", 85,  5, "warning",  "infra-team"),
]

def evaluate_rules(df, rules=RULES):
    """Return one alert per continuous breach (de-duplicated), not one per minute."""
    alerts = []
    for name, metric, op, thr, dur, sev, route in rules:
        breach = (df[metric] > thr) if op == ">" else (df[metric] < thr)
        group = (breach != breach.shift()).cumsum()
        for _, seg in df[breach].groupby(group[breach]):
            if len(seg) >= dur:                               # must last long enough
                fire_at = seg["timestamp"].iloc[dur - 1]      # fires after `dur` minutes
                alerts.append({"alert": name, "severity": sev, "route": route,
                               "fired_at": fire_at, "breach_start": seg["timestamp"].iloc[0],
                               "breach_end": seg["timestamp"].iloc[-1],
                               "peak_value": round(seg[metric].max(), 1), "threshold": thr})
    return pd.DataFrame(alerts).sort_values("fired_at").reset_index(drop=True) if alerts else pd.DataFrame(
        columns=["alert","severity","route","fired_at","breach_start","breach_end","peak_value","threshold"])

def group_alerts(alerts, gap_minutes=10):
    """Noise reduction: merge alerts firing within gap_minutes into one incident group."""
    if alerts.empty:
        return alerts.assign(group_id=[])
    a = alerts.sort_values("fired_at").copy()
    new = a["fired_at"].diff() > pd.Timedelta(minutes=gap_minutes)
    a["group_id"] = new.cumsum() + 1
    return a

if __name__ == "__main__":
    m = pd.read_csv("metrics/metrics.csv", parse_dates=["timestamp"])
    a = group_alerts(evaluate_rules(m))
    a.to_csv("alerts/alerts.csv", index=False)
    print(a.to_string(index=False))
    print(f"\n{len(a)} alerts -> {a['group_id'].nunique() if len(a) else 0} incident group(s)")
