# AIOps Risk Register

| # | Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|
| 1 | Logs contain personal data (user_id, names) sent to an AI tool | Medium | High | Use only synthetic/masked data; scrub IDs before any AI use | Data owner |
| 2 | Detector flags normal traffic spikes (false positives) -> alert fatigue | High | Medium | Require 3-minute runs, tune thresholds, review precision monthly | AIOps engineer |
| 3 | Detector misses a slow degradation (false negatives) | Medium | High | Add trend/capacity checks; keep static threshold alerts as a backstop | AIOps engineer |
| 4 | Automated remediation makes an outage worse | Low | High | No auto-remediation; all actions human-approved (see policy) | Incident manager |
| 5 | AI-generated summary states something untrue | Medium | Medium | Validate every claim against source data (Day 14 table) | Reviewer |
| 6 | Baseline contamination: long incident becomes "normal" | Medium | High | Exclude flagged points from baseline (implemented) | AIOps engineer |
| 7 | Too-broad access for the pipeline | Low | High | Read-only access; least privilege; audit logs of every run | Security |
| 8 | Model/threshold drift as the system changes | High | Medium | Re-evaluate after each release; keep labelled test data | AIOps engineer |
