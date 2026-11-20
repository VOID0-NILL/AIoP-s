# AIOps Capstone - College Portal Incident Detection

**Problem:** When the College Portal slows down, the team drowns in logs and metrics.
This prototype detects the abnormal period, raises a de-duplicated alert, correlates logs,
metrics and events, and writes an incident report with ranked, evidence-based causes.
Everything uses **synthetic, fictional data** - no real systems are touched.

## Run it (Linux, Python 3.10+)
```bash
python3 -m venv venv && source venv/bin/activate
pip install pandas numpy matplotlib
python3 src/generate_data.py      # creates logs/, metrics/, events/, labels/ (seeded: same data every time)
python3 src/pipeline.py           # runs the whole pipeline
python3 src/slo.py                # SLI / error budget
python3 src/health_check.py --at "2026-11-20 14:20:00"; echo $?    # exit code 2 = CRITICAL
python3 -m unittest discover -s tests -v                            # 12 tests
```

## Data flow
`generate_data.py` -> logs / metrics / events -> `parse_logs.py` -> `detect_anomalies.py` (rolling z-score)
-> `alerts.py` (rules + grouping) -> `incident_report.py` (timeline + ranked hypotheses) -> `reports/`

## Outputs
`reports/log_findings.md` - `reports/incident_report.md` - `reports/correlated_timeline.csv` - `reports/slo_report.md`
`alerts/alerts.csv` - `charts/anomalies.png` - `metrics/metrics_with_anomalies.csv`

## Results (synthetic data, seed 42)
- Detection vs ground truth: precision 1.0, recall 1.0 (50 incident minutes)
- With 6x noisier latency: precision 1.0, recall 0.98
- Alerts: 2 alerts merged into 1 incident group
- Pipeline run time: well under 1 second

## Limitations (read before trusting)
- Perfect scores come from clean synthetic data with one injected incident; real data will be messier.
- Evidence scores are rule weights, not probabilities; correlation in time is not proof of cause.
- Thresholds (z=4, 3-minute runs, 800 ms, 5%) are chosen by hand and need tuning on real data.
- No auto-remediation by design: see `docs/human_approval_policy.md`.

## Folders
`src/` code - `tests/` tests - `docs/` runbooks, risk register, approval policy - `reports/` and `charts/` outputs
