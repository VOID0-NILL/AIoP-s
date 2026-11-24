# Day 14 - AI Summary Validation Table

AI tool: Claude (Anthropic), claude.ai chat. Input: reports/ai_input.txt (synthetic data). Output: reports/ai_summary.txt.
Automatic first pass: python3 src/check_summary.py found 28 of 30 items; the 2 not found (9 and 10 minutes) are calculated values, checked by hand below.

| # | Claim in AI output | Source line / file | Correct? | Fix or note |
|---|---|---|---|---|
| 1 | Breach 14:07 to 14:54, 48 minutes | ai_input.txt, "Breach window" line | Yes | |
| 2 | Latency rose from 217.8 ms to 2259.0 ms | Metrics section, latency_ms line | Yes | |
| 3 | Error rate rose from 0.6% to 21.7% | Metrics section, error_rate_percent line | Yes | |
| 4 | Errors came from fee-service, app-server and web-server | Timeline, "first ERROR" lines | Yes | |
| 5 | HighLatency and HighErrorRate both fired at 14:09 | Alerts section | Yes | |
| 6 | fee-service v2.3 deployed at 13:58 | Timeline, 13:58:00 | Yes | |
| 7 | Rollback to v2.2 at 14:45 | Timeline, 14:45:00 | Yes | |
| 8 | First 502 Bad Gateway on web-server at 14:05:00 | Timeline, 14:05:00 | Yes | |
| 9 | First "Connection pool exhausted (max=20)" on fee-service at 14:06:11 | Timeline, 14:06:11 | Yes | |
| 10 | First "DB connection timeout after 30s" on fee-service at 14:06:51 | Timeline, 14:06:51 | Yes | |
| 11 | Database event at 14:55:00: connection pool back to normal | Timeline, 14:55:00 | Yes | |
| 12 | Breach window ends at 14:54:00 | "Breach window" line | Yes | |
| 13 | Deploy was 9 minutes before the breach (13:58 to 14:07) | Calculated from timeline and breach window | Yes | Calculated, not in source |
| 14 | Request rate fell from 976 to an average of 745 per minute | Metrics section, request_rate_per_min line | Yes | |
| 15 | A traffic surge is unlikely | Follows from row 14 (rate fell) | Yes | Interpretation, reasonable |
| 16 | The deploy hypothesis is supported by timing and fee-service errors | Rows 6, 9 and 13 | Yes, as a hypothesis | Data shows timing only, not proof |
| 17 | Pool-exhaustion hypothesis is supported by the errors and the 14:55 event | Rows 9, 10 and 11 | Yes | |
| 18 | Recovery came 10 minutes after the rollback (14:45 to 14:55) | Calculated from timeline | Yes | Calculated, not in source |
| 19 | First-error times of the services are within about two minutes | Timeline: 14:05:00 (web-server) to 14:07:37 (app-server) | Partly | The gap is 2 min 37 s, so "about 2.5 minutes" is more accurate |
| 20 | notification-service timeouts at 13:43:10 (x5) came before the deploy and are not linked | Timeline, 13:43:10 | Yes | |
| 21 | "High latency alert fired" event at 14:07 and HighLatency alert at 14:09 are two records | Timeline, 14:07:00 and 14:09:00 | Yes | |
| 22 | Number of failed fee payments is not in the data | Whole ai_input.txt | Yes | |

Result: 21 Yes (one as a hypothesis), 1 Partly, 0 No.

## What I learned from this check
(write 2-3 lines in your own words: what the AI got right, what needed a closer look, and why a human check is still needed)
