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
| Recall, noisy latency (6x) | 0.98 | test output |
| Tests passing | 12 of 12 | test output |
| Processing time (whole pipeline) | 0.56 seconds | pipeline output |
| Alerts | 2 alerts in 1 group | pipeline output |

## 3. Bug and issue log

| # | What went wrong | How it was found | What I changed | Result after fix |
|---|---|---|---|---|
| 1 | The first anomaly detector missed most of the incident. During a long incident its rolling baseline kept absorbing the broken values and started treating them as normal. | Comparing the flagged minutes with the ground-truth labels gave recall of only 0.12. | Points flagged as unusual are no longer added to the baseline, so the baseline stays at the last known-normal behaviour. | Recall 1.0, precision 1.0 on the clean data; 0.98 recall with noisier latency. |
| 2 | The AI-summary checker accepted "9 minutes" as found in the source, although that number was calculated and not in the data. | Reading the checker output by hand: the other calculated number (10 minutes) was flagged but 9 minutes was not. | The check now matches the number and its unit as a whole, instead of a plain substring (the "9" was matching inside "2259.0"). | Both calculated numbers are flagged; a wrong unit (for example "2259 minutes") is flagged too. |

## 4. Failure cases and limits
I tested these on 21 Nov by injecting artificial data; they are not from real systems.
- Slow drift: when latency grew by 600 ms over 8 hours, none of 480 minutes was flagged, because the baseline follows the slow change. A trend or static threshold alert is needed for this.
- Short real incidents: a 2-minute error burst is not flagged, because the 3-minute rule that removes one-off spikes also hides short real events.
- The thresholds (z = 4, 3 minutes, 800 ms, 5%) were chosen by hand on one synthetic day; real data may need retuning, and the perfect scores come from clean data with one obvious incident.

## 5. Two weaknesses improved
1. Detector baseline contamination (Bug 1): recall went from 0.12 to 1.0.
2. Checker substring matching (Bug 2): calculated numbers and wrong units are now caught.
