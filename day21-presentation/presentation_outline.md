# Final Presentation Outline - AIOps Capstone (7-10 minutes)

Audience: an IT operations manager. Goal: show I understand the problem, built something that works,
tested it honestly, and know its limits. Disclose up front that an AI assistant (Claude) helped me write code.

## Slide plan (about 9 minutes + 1 minute live demo)

| # | Slide | Time | What to say | Show |
|---|---|---|---|---|
| 1 | Title | 0:30 | Name, project: incident detection for a College Portal | - |
| 2 | The problem | 1:00 | Ops teams drown in logs, metrics and alerts. When the portal slows, who finds the cause, and how fast? | one line of raw log |
| 3 | Design / data flow | 1:00 | Logs, metrics, events -> parse -> detect -> alert -> correlate -> report -> human approves | day01-foundations/dataflow.png |
| 4 | Data and the incident | 0:45 | Synthetic, seeded data (same data every run). One injected incident: deploy 13:58, breach 14:07-14:54, rollback 14:45 | metric_dictionary table |
| 5 | Detection | 1:15 | Rolling z-score on latency and error rate. Needs 3 minutes in a row. Baseline ignores flagged points | charts/anomalies.png |
| 6 | Alerts and correlation | 1:15 | Rules with duration and routing: 2 alerts merged into 1 incident group. Timeline plus ranked causes, labelled hypotheses | report timeline |
| 7 | Dashboard and reliability | 0:45 | 6 indicators with units. SLI 96.67% vs SLO 99.5%, error budget used up | charts/dashboard.png |
| 8 | Evaluation | 1:00 | Precision 1.0 and recall 1.0 on clean data; recall 0.98 with 6x noisier latency; 12 tests; runs in well under 1 second | test output |
| 9 | Risks and governance | 0:45 | No auto-remediation; approval table; AI summaries checked claim by claim | docs/human_approval_policy.md |
| 10 | Limits, next steps, lessons | 0:45 | Synthetic data is easy; thresholds are hand-picked; next: real logs, tuning, seasonality | - |

Live demo (1 minute): run `python3 src/pipeline.py`, then open reports/incident_report.md.

## Five key technical decisions (say each in 2-3 sentences)

1. **Seeded synthetic dataset with ground-truth labels.** Safe (no real data), reproducible by anyone, and labels let me measure precision and recall.
2. **Rolling z-score with a "clean" baseline plus a 3-minute rule.** My first version had recall 0.12: during a long incident the baseline learned the broken values as normal. Excluding flagged points from the baseline fixed it (recall 1.0). The 3-minute rule stops one-off spikes from alerting.
3. **Alerts with duration and grouping.** Alerts fire only after 3-5 minutes of breach, and alerts close in time are merged: 2 alerts became 1 incident group. This reduces noise.
4. **Rule-based, explainable correlation instead of a black-box model.** Each cause hypothesis has an evidence score and cites its evidence. Correlation in time is not proof, so the report says "hypothesis", not "cause".
5. **Human-approved remediation and verified AI output.** The pipeline never changes a system. AI summaries are checked against the source: my checker even had a bug (it wrongly accepted "9 minutes") that I found and fixed.

## What I learned (pick 3 for the last slide)
- A perfect score on clean synthetic data proves little; testing with noise, missing values and spikes matters.
- A static threshold (disk 85%) can fire on a disk that is full but not growing; trend forecasts (Day 15) add what thresholds cannot.
- Automatic checks can be wrong too, so a human review step is needed.

## Questions to expect, and honest answers
- Why is your recall 1.0? - The data is clean and synthetic with one obvious incident. With 6x noise recall was 0.98. Real data will be harder.
- How did you choose z = 4 and 3 minutes? - By hand, to avoid false alarms on this data. On real data I would tune them using labelled past incidents.
- Why not machine learning? - For one metric with a clear baseline a simple method is explainable and testable. ML would need much more data.
- Can this fix problems automatically? - No, by design. Rollback and restarts need human approval (see the approval policy).
- What does the correlation prove? - Only that events happened close together. A code or config diff is needed to confirm the cause.
- What would you do next? - Test on real logs, handle daily traffic cycles, add trend-based alerts, connect to Grafana.
- Did you write this alone? - I used an AI assistant (Claude) to help build the code and documents. I ran it, tested it, and can explain each file. Keep this answer true: only say it if you can back it up.

## Before the day
- [ ] Practise out loud 2-3 times with a timer (target 9 minutes)
- [ ] Run the demo once on your VM and keep the output files ready as backup
- [ ] Be able to explain each src/ file in 1-2 sentences
- [ ] Tracker complete: real hours, dates, GitHub links, self scores, Source Log
