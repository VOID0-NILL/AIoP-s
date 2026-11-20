"""
generate_data.py - builds ONE synthetic dataset for the College Portal.
Used by every later day: parsing, anomaly detection, alerts, correlation, RCA, capstone.

Creates:
  logs/portal.log               application log (one line per record)
  metrics/metrics.csv           1-minute metrics for 24 hours
  events/events.csv             deploys / restarts / rollback
  labels/incident_labels.csv    ground truth (for precision/recall on Day 19)

All data is fictional. Same SEED = same data (reproducible).
"""
import csv, math, os, random
from datetime import datetime, timedelta

SEED = 42
START = datetime(2026, 11, 20, 0, 0, 0)
MINUTES = 24 * 60

# --- Simulated incident (ground truth) ---------------------------------------
DEPLOY_AT   = START + timedelta(hours=13, minutes=58)   # fee-service v2.3 deployed
INC_START   = START + timedelta(hours=14, minutes=5)    # DB connection pool exhausted
ROLLBACK_AT = START + timedelta(hours=14, minutes=45)   # rollback to v2.2
INC_END     = START + timedelta(hours=14, minutes=55)   # recovery complete

random.seed(SEED)
for d in ("logs", "metrics", "events", "labels"):
    os.makedirs(d, exist_ok=True)

def in_incident(t):
    return INC_START <= t < INC_END

def daily_load(t):
    """0..1 curve: low at night, peak around midday."""
    h = t.hour + t.minute / 60
    return 0.5 - 0.5 * math.cos(2 * math.pi * (h - 2) / 24)

# --- 1. Metrics ---------------------------------------------------------------
with open("metrics/metrics.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["timestamp", "cpu_percent", "memory_percent", "disk_percent",
                "latency_ms", "request_rate_per_min", "error_rate_percent"])
    for m in range(MINUTES):
        t = START + timedelta(minutes=m)
        load = daily_load(t)
        cpu = 20 + 30 * load + random.gauss(0, 2)
        mem = 45 + 10 * load + random.gauss(0, 1) + m * 0.002
        disk = 61 + m * 0.001 + random.gauss(0, 0.05)
        lat = 120 + 80 * load + random.gauss(0, 10)
        req = 200 + 800 * load + random.gauss(0, 30)
        err = max(0.0, 0.5 + random.gauss(0, 0.2))
        if in_incident(t):
            k = min(1.0, (t - INC_START).total_seconds() / 300)  # ramps up in 5 min
            cpu += 35 * k; mem += 15 * k
            lat += 1800 * k + random.gauss(0, 150)
            err += 18 * k + random.gauss(0, 2)
            req *= 0.75
        w.writerow([t.strftime("%Y-%m-%d %H:%M:%S"), round(cpu, 1), round(mem, 1),
                    round(disk, 2), round(max(lat, 20), 0), round(max(req, 0), 0),
                    round(max(err, 0), 2)])

# --- 2. Events ----------------------------------------------------------------
events = [
    (START + timedelta(hours=2),  "maintenance", "database",   "Nightly backup started"),
    (START + timedelta(hours=2, minutes=30), "maintenance", "database", "Nightly backup completed"),
    (START + timedelta(hours=9),  "deploy",      "web-server", "Deployed web-server v1.8"),
    (DEPLOY_AT,                   "deploy",      "fee-service","Deployed fee-service v2.3"),
    (INC_START + timedelta(minutes=2), "alert",  "database",   "High latency alert fired"),
    (INC_START + timedelta(minutes=5), "alert",  "app-server", "High error rate alert fired"),
    (ROLLBACK_AT,                 "rollback",    "fee-service","Rolled back fee-service to v2.2"),
    (INC_END,                     "recovery",    "database",   "Connection pool back to normal"),
]
with open("events/events.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["timestamp", "event_type", "service", "description"])
    for t, typ, svc, desc in sorted(events):
        w.writerow([t.strftime("%Y-%m-%d %H:%M:%S"), typ, svc, desc])

# --- 3. Logs ------------------------------------------------------------------
NORMAL = [
    ("INFO", "login-service", "auth",     "User login success user_id={u}"),
    ("INFO", "web-server",    "http",     "GET /results/{u} 200 {ms}ms"),
    ("INFO", "fee-service",   "payment",  "Fee payment accepted user_id={u} amount=15000"),
    ("INFO", "web-server",    "http",     "GET /home 200 {ms}ms"),
    ("INFO", "app-server",    "session",  "Session created user_id={u}"),
]
BACKGROUND_WARN = [
    ("WARN", "login-service", "auth",     "Failed login attempt user_id={u}"),
    ("WARN", "web-server",    "http",     "Slow response {ms}ms on /results/{u}"),
]
BACKGROUND_ERR = [
    ("ERROR", "web-server", "http",   "404 page not found /old-timetable"),
    ("ERROR", "app-server", "api",    "Request timeout calling notification-service"),
]
INCIDENT = [
    ("ERROR", "fee-service", "database", "DB connection timeout after 30s"),
    ("ERROR", "fee-service", "database", "Connection pool exhausted (max=20)"),
    ("WARN",  "database",    "query",    "Slow query detected duration=4200ms"),
    ("ERROR", "app-server",  "api",      "Upstream fee-service returned 500"),
    ("ERROR", "web-server",  "http",     "502 Bad Gateway /fee/pay"),
]
lines = []
for m in range(MINUTES):
    t = START + timedelta(minutes=m)
    n = int(2 + 8 * daily_load(t))                    # normal records per minute
    for _ in range(n):
        r = random.random(); u = random.randint(1000, 9999); ms = random.randint(40, 400)
        if r < 0.03:   lvl, svc, comp, msg = random.choice(BACKGROUND_WARN)
        elif r < 0.04: lvl, svc, comp, msg = random.choice(BACKGROUND_ERR)
        else:          lvl, svc, comp, msg = random.choice(NORMAL)
        ts = t + timedelta(seconds=random.randint(0, 59), milliseconds=random.randint(0, 999))
        lines.append((ts, lvl, svc, comp, msg.format(u=u, ms=ms)))
    if in_incident(t):
        k = min(1.0, (t - INC_START).total_seconds() / 300)
        for _ in range(int(3 + 12 * k)):
            lvl, svc, comp, msg = random.choice(INCIDENT)
            ts = t + timedelta(seconds=random.randint(0, 59), milliseconds=random.randint(0, 999))
            lines.append((ts, lvl, svc, comp, msg))
# one repeated noisy message all day (useful for noise-reduction on Day 9)
for m in range(0, MINUTES, 3):
    t = START + timedelta(minutes=m, seconds=random.randint(0, 59))
    lines.append((t, "WARN", "web-server", "cache", "Cache miss ratio high on /static/logo.png"))
# deploy markers also written to the log
lines.append((DEPLOY_AT, "INFO", "fee-service", "deploy", "Deployment started version=2.3"))
lines.append((ROLLBACK_AT, "WARN", "fee-service", "deploy", "Rollback started version=2.2"))

lines.sort(key=lambda x: x[0])
with open("logs/portal.log", "w") as f:
    for ts, lvl, svc, comp, msg in lines:
        f.write(f"{ts.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} | {lvl:<5} | {svc} | {comp} | {msg}\n")

# --- 4. Ground-truth labels ---------------------------------------------------
with open("labels/incident_labels.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["incident_id", "start", "end", "root_cause", "affected_services"])
    w.writerow(["INC-001", INC_START.strftime("%Y-%m-%d %H:%M:%S"), INC_END.strftime("%Y-%m-%d %H:%M:%S"),
                "fee-service v2.3 exhausted DB connection pool", "fee-service;database;app-server;web-server"])

print(f"logs/portal.log      : {len(lines)} lines")
print(f"metrics/metrics.csv  : {MINUTES} rows")
print(f"events/events.csv    : {len(events)} events")
print("labels/incident_labels.csv : 1 incident (INC-001)")
