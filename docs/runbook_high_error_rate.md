# Runbook 1 - HighErrorRate / HighLatency (critical)

**Trigger:** error rate > 5% or latency > 800 ms for 3+ minutes (alerts.py).
**Impact:** students cannot pay fees or see results (College Portal).
**Owner:** oncall-app-team. **Mode:** simulated - do not run changes on live systems.

## 1. Validate (read-only)
1. `python3 src/health_check.py --at "<alert time>"` -> exit code 2 confirms CRITICAL.
2. Check `reports/log_findings.md`: which service has the most ERROR lines?
3. Check `events/events.csv`: any deploy or change in the 30 minutes before the alert?

## 2. Safe actions (need human approval first)
- If a deploy happened just before: propose **rollback of that service** to the previous version.
- If errors mention a database: check connection counts (read-only) before any restart.
- Post a status message to the team channel.

## 3. Stop conditions / rollback
- Stop and escalate if errors rise after the action, or if more than one service is affected.
- Never restart the database without DBA approval.

## 4. Escalation
- 15 min with no improvement -> escalate to the senior on-call. 30 min -> incident manager.

## 5. Verify and close
- Alert clears and error rate < 1% for 10 minutes. Record the cause in the incident report.
