# Metric Dictionary - College Portal (Day 5)

All numbers come from the synthetic 24-hour dataset (`metrics/metrics.csv`, seed 42). "Normal" means the whole day outside the incident window (14:05-14:55).

## Metric vs event vs alert vs log

| Term | Meaning | College Portal example |
|---|---|---|
| **Metric** | A number measured over time, sampled at regular intervals | CPU % every minute; latency in ms |
| **Event** | Something that happened at a point in time (a change or a state change) | "Deployed fee-service v2.3" at 13:58 |
| **Alert** | A notification created when a rule says a metric or event needs attention | "HighLatency (critical)" fired at 14:09 |
| **Log** | A text record of what a service did | `ERROR - Connection pool exhausted (max=20)` |

A metric is raw measurement, an alert is a *decision* made from it, and an event gives *context* (what changed).

## Metrics

| Metric (column) | Unit | What it measures | Why it matters | Normal range (min - p95 - max) | Peak in incident |
|---|---|---|---|---|---|
| `latency_ms` | milliseconds | Time to answer a request | Users feel slowness first | 93 - 204 - 227 | 2259 |
| `error_rate_percent` | % of requests | Share of requests that fail | Direct measure of broken service | 0.0 - 0.8 - 1.1 | 21.7 |
| `cpu_percent` | % of capacity | Processor busy time | High CPU = slow responses, no headroom | 15 - 50 - 56 | 90.5 |
| `memory_percent` | % of capacity | RAM in use | Full memory causes swapping or crashes | 43 - 57 - 59 | 73.9 |
| `request_rate_per_min` | requests per minute | Traffic reaching the portal | Separates "more users" from "something broke" | 106 - 992 - 1056 | 788 (it fell) |
| `disk_percent` | % of capacity | Storage used | A full disk stops writes and logs | 60.9 - 62.4 - 62.5 | 62.0 |

## Thresholds and rationale

| Metric | Warning | Critical / alert | Duration | Why this number |
|---|---|---|---|---|
| `latency_ms` | 500 | 800 (alert), 1000 (health check) | 3 min | About 4x the highest normal value (227) - well above daily variation, still early enough to act |
| `error_rate_percent` | 2 | 5 | 3 min | Normal never exceeds 1.1%; 5% means 1 in 20 users is failing |
| `cpu_percent` | 70 | 85 | 5 min | Normal peaks near 56%; above 85% there is little room for a traffic spike |
| `memory_percent` | 80 | 90 | - | Leaves a buffer before swapping; normal stays under 60% |
| `disk_percent` | 80 | 85 (alert), 90 (health check) | 5 min | Leaves time to clean up before 100%; a *trend* alert is better (see Day 15) |
| `request_rate_per_min` | - | none | - | Context metric: a fall during errors suggests failures, not a traffic surge |

**Why a duration?** A single bad minute is often a spike. Requiring 3-5 minutes in a row cuts false alarms (see `tests/test_pipeline.py`, `test_short_breach_does_not_fire`).

## Limits of these thresholds
- They are chosen by hand from one synthetic day; real systems need tuning with weeks of data.
- Daily traffic changes the normal level (night vs midday), so a fixed number is only a first approximation - the anomaly detector (Day 8) adapts to recent behaviour instead.
- Static thresholds do not catch slow growth; use trend forecasts for disk and memory.
