# Day 19 - Testing, Evaluation and Improvement

## 1. Test plan
Run: `python3 -m unittest discover -s tests -v` (12 tests)

| Scenario | Test name | What should happen |
|---|---|---|
| Normal data | test_normal_data_has_no_anomalies | No anomaly flagged |
| Abnormal data | test_incident_is_detected | Precision and recall of at least 0.9 |
| Missing data | test_missing_values_do_not_crash | No crash; incident still found |
| Noisy data | test_noisy_data_reports_metrics | Recall of at least 0.8 with 6x noisier latency |
| One-off spike | test_single_spike_is_not_flagged | Not flagged (needs 3 minutes in a row) |
| Short breach | test_short_breach_does_not_fire | No alert for a 2-minute breach |
| Alert grouping | test_incident_fires_and_groups_into_one | 2 or more alerts merged into 1 group |
| Health check | test_exit_codes, test_missing_file_returns_3 | Exit codes 0, 1, 2, 3 are correct |
| Parser | test_valid_line, test_malformed_line_returns_none | Valid line parsed; bad line skipped |

## 2. Results table (my own run)

| Check | Result | Source |
|---|---|---|
| Precision, clean data | 1.0 | pipeline output |
| Recall, clean data | 1.0 | pipeline output |
| Recall, noisy latency (6x) | 0.56 | test output |
| Tests passing | 12 of 12 | test output |
| Processing time (whole pipeline) | (write the total from your run, in seconds) | pipeline output |
| Alerts | 2 alerts in 1 group | pipeline output |

## 3. Bug and issue log

| # | What went wrong | How it was found | What I changed | Result after fix |
|---|---|---|---|---|
| 1 | (write in your own words: the detector's baseline) | | | |
| 2 | (write in your own words: the AI summary checker accepted "9 minutes") | | | |

Hints for the bug log, to explain in your own words:
- Bug 1: the first detector version had recall 0.12. During a long incident the rolling baseline learned the broken values as normal. After the fix, flagged points are kept out of the baseline and recall became 1.0.
- Bug 2: the checker looked for a number as a plain substring, so "9" matched inside "2259.0". After the fix it matches number and unit as a whole.

## 4. Failure cases and limits (2-3 lines of your own)
(Think: what kinds of data would still fool this detector? Example: slow gradual growth, or a daily peak that looks unusual.)

## 5. Two weaknesses improved
1. (Bug 1 above)
2. (Bug 2 above)
