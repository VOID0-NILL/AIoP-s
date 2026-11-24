"""Day 13 - SIMULATED execution of the two runbooks on our mock data.
Nothing real is changed: actions only update a mock dictionary, and every risky step waits for human approval.
Usage:  python3 src/simulate_runbook.py            (stops at the approval step)
        python3 src/simulate_runbook.py --approve  (simulates an approved rollback and verifies recovery)"""
import sys
import pandas as pd
sys.path.insert(0, "src")
from health_check import check_row
from parse_logs import parse_file

def say(msg=""): print(msg)

def runbook_high_error_rate(approve):
    say("=== RUNBOOK 1: HighErrorRate / HighLatency (SIMULATION) ===")
    m = pd.read_csv("metrics/metrics.csv", parse_dates=["timestamp"])
    ev = pd.read_csv("events/events.csv", parse_dates=["timestamp"])
    al = pd.read_csv("alerts/alerts.csv", parse_dates=["fired_at", "breach_start", "breach_end"])
    logs, _ = parse_file("logs/portal.log")
    t = al["fired_at"].min()
    say(f"Trigger: alert fired at {t}")
    say("\n[1] VALIDATE (read-only)")
    code, findings = check_row(m[m["timestamp"] == t].iloc[0].to_dict())
    say(f"    health check at alert time -> {['OK', 'WARNING', 'CRITICAL'][code]} (exit code {code})")
    for f in findings:
        if "OK" not in f: say(f"      {f}")
    win = logs[(logs["timestamp"] >= t - pd.Timedelta(minutes=10)) & (logs["timestamp"] <= t) & (logs["level"] == "ERROR")]
    top = win["service"].value_counts()
    say(f"    most ERROR lines in the 10 minutes before the alert: {top.index[0]} ({int(top.iloc[0])} lines)")
    dep = ev[(ev["event_type"] == "deploy") & (ev["timestamp"] <= t) & (ev["timestamp"] >= t - pd.Timedelta(minutes=30))]
    if dep.empty:
        say("    no deploy in the previous 30 minutes -> stop here and escalate (no rollback proposal)"); return
    d = dep.iloc[-1]
    say(f"    recent change: '{d['description']}' at {d['timestamp']}")
    say("\n[2] SAFE ACTION (needs human approval)")
    say(f"    Proposed: roll back {d['service']} to the previous version.")
    say("    APPROVAL REQUIRED: incident manager (see docs/human_approval_policy.md)")
    if not approve:
        say("    Status: waiting for approval. NO ACTION TAKEN."); return
    mock = {"fee-service": "v2.3"}
    say("    Simulated approval: GRANTED (mock). Applying rollback to the MOCK state only...")
    mock["fee-service"] = "v2.2"
    say(f"    mock state is now: {mock}")
    say("\n[3] STOP CONDITIONS")
    say("    Stop and escalate if errors rise after the action or more than one service is affected.")
    after = m[m["timestamp"] >= ev[ev["event_type"] == "recovery"]["timestamp"].iloc[0]].iloc[0]
    c2, _ = check_row(after.to_dict())
    say(f"\n[4] VERIFY (uses recorded data after recovery at {after['timestamp']})")
    say(f"    health check -> {['OK', 'WARNING', 'CRITICAL'][c2]}; error rate {after['error_rate_percent']}%, latency {after['latency_ms']} ms")
    say("    Close only after the alert stays clear for 10 minutes. Record the cause in the incident report.")

def runbook_disk(mock_disk=89):
    say("\n=== RUNBOOK 2: DiskAlmostFull (SIMULATION, mock values) ===")
    say(f"Trigger: mock disk usage {mock_disk}% (alert threshold 85%)")
    say("\n[1] VALIDATE (read-only)")
    code, _ = check_row({"cpu_percent": 30, "memory_percent": 50, "disk_percent": mock_disk, "latency_ms": 100, "error_rate_percent": 0.1})
    say(f"    health check -> {['OK', 'WARNING', 'CRITICAL'][code]} (exit code {code})")
    mock_dirs = {"/usr": 12.0, "/opt": 0.45, "/var/log": 0.19, "/home": 0.43}
    say("    mock du result (GB): " + ", ".join(f"{k} {v}" for k, v in sorted(mock_dirs.items(), key=lambda kv: -kv[1])))
    say("    biggest folder is /usr (installed software), not logs -> growth is not from logs")
    say("\n[2] SAFE ACTION (needs human approval)")
    say("    Do NOT delete files by hand. Only propose: rotate/compress old logs after confirming backups.")
    say("    APPROVAL REQUIRED: infra-team lead. NO ACTION TAKEN.")
    say("\n[3] STOP / ESCALATE")
    say("    Disk above 95% -> treat as critical and page infra on-call; growth still rising after cleanup -> request more disk.")
    say("\n[4] VERIFY: disk below 75% and the growth trend understood (see reports/capacity_report.md)")

if __name__ == "__main__":
    runbook_high_error_rate("--approve" in sys.argv)
    runbook_disk()
