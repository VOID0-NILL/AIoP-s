# Human Approval Policy

| Action | Who may do it | Approval needed? |
|---|---|---|
| Read logs, metrics, dashboards | Pipeline / any engineer | No (read-only) |
| Generate alerts and incident summaries | Pipeline | No, but a human reviews the summary |
| Post status update | On-call engineer | No |
| Roll back a deploy | On-call engineer | **Yes** - incident manager |
| Restart a service | On-call engineer | **Yes** - service owner |
| Restart / change a database | DBA | **Yes** - DBA lead + incident manager |
| Delete data or logs | Nobody automatically | **Yes** - written approval |
| Change alert thresholds | AIOps engineer | **Yes** - peer review |

Rules: every action is logged (who, when, why); the pipeline never executes remediation by itself; AI output is a suggestion, never an order.

## Data-handling checklist
- [ ] Only synthetic or approved data used
- [ ] No credentials, tokens or personal data in logs sent to public AI tools
- [ ] Every AI-generated claim checked against the source
- [ ] Access is read-only and logged
