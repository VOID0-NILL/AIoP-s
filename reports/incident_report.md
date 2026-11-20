# Incident Report - College Portal

> Generated automatically from sample data. Causes below are **hypotheses ranked by evidence**, not confirmed facts.

## Summary
- Breach window: **2026-11-20 14:07:00** to **2026-11-20 14:54:00** (about 48 minutes)
- Alerts: HighErrorRate, HighLatency (2 alerts, grouped into 1 incident)
- Affected services (from ERROR logs): app-server, fee-service, web-server

## Impact (normal level before incident -> peak during incident)
- latency_ms: 217.8 -> 2259.0
- error_rate_percent: 0.6 -> 21.7
- cpu_percent: 50.2 -> 90.5
- memory_percent: 56.8 -> 73.9

## Timeline (symptoms and signals in time order)

| Time | Source | Where | What |
|---|---|---|---|
| 2026-11-20 13:43:10 | log | app-server | first ERROR 'Request timeout calling notification-service' (x5) |
| 2026-11-20 13:58:00 | event | fee-service | deploy: Deployed fee-service v2.3 |
| 2026-11-20 14:05:00 | log | web-server | first ERROR '502 Bad Gateway /fee/pay' (x157) |
| 2026-11-20 14:06:11 | log | fee-service | first ERROR 'Connection pool exhausted (max=20)' (x143) |
| 2026-11-20 14:06:51 | log | fee-service | first ERROR 'DB connection timeout after 30s' (x141) |
| 2026-11-20 14:07:00 | event | database | alert: High latency alert fired |
| 2026-11-20 14:07:37 | log | app-server | first ERROR 'Upstream fee-service returned 500' (x139) |
| 2026-11-20 14:09:00 | alert | oncall-app-team | HighLatency (critical) peak=2259.0 |
| 2026-11-20 14:09:00 | alert | oncall-app-team | HighErrorRate (critical) peak=21.7 |
| 2026-11-20 14:10:00 | event | app-server | alert: High error rate alert fired |
| 2026-11-20 14:45:00 | event | fee-service | rollback: Rolled back fee-service to v2.2 |
| 2026-11-20 14:55:00 | event | database | recovery: Connection pool back to normal |

## Symptoms vs likely causes
- **Symptoms:** high latency, high error rate, 502/500 responses (what users and alerts see).
- **Candidate causes:** see ranked hypotheses below (what may have produced the symptoms).

## Root-cause hypotheses (ranked by evidence score)

### H1. Change-induced regression (new deploy) - evidence score 7
- Deploy 'Deployed fee-service v2.3' at 2026-11-20 13:58:00, 9 min before breach start
- 277 ERROR lines come from the deployed service (fee-service)
- Rollback at 2026-11-20 14:45:00; breach ended 2026-11-20 14:54:00 (metrics recovered after the rollback)
- Next diagnostic step: Compare v2.3 vs v2.2 diff; check release notes and config changes.

### H2. Database connection-pool exhaustion - evidence score 4
- 277 ERROR lines mention connection pool exhaustion / DB timeouts
- 128 slow-query warnings from the database
- Next diagnostic step: Check pool size, open connections per service, connection leaks in the new code.

### H3. Traffic surge / capacity limit - evidence score 0
- No traffic surge: request rate 976 before vs 745 during (it fell)
- Next diagnostic step: Compare with last week's same-hour traffic; check autoscaling limits.

### H4. External dependency (notification-service) - evidence score 0
- notification-service timeouts stayed at their normal background rate
- Next diagnostic step: Check dependency status page only if other causes are ruled out.

> Note: H1 and H2 are not mutually exclusive. The deploy may be the trigger and pool exhaustion the mechanism.

## Suggested next steps (human-approved)
1. Keep fee-service on v2.2 until the v2.3 connection handling is reviewed.
2. Review connection-pool settings and open-connection counts for the new release.
3. Add a pre-deploy check/canary for fee-service so this is caught at 5% traffic.
4. Hold a short post-incident review; record the confirmed cause.

## Limitations
- Synthetic data: one injected incident; real systems are noisier.
- Evidence scores are simple rule weights (not probabilities); they rank, they do not prove.
- Correlation in time does not prove causation; confirm with a code/config diff before closing.