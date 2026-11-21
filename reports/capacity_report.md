# Capacity forecast - disk usage

- Data: 30 daily readings, 2026-10-22 to 2026-11-20 (fictional sample unless you replaced it with real readings)
- Latest reading: **72.6%**; trend-line level today: 72.1%
- Linear trend: **+0.32 percentage points per day** (approx. range +0.29 to +0.36)

## When will the threshold be reached? (from today)

| Threshold | Best estimate | Fast case | Slow case | Estimated date |
|---|---|---|---|---|
| warning 85% | 40 days | 36 days | 44 days | 2026-12-29 |
| critical 90% | 55 days | 50 days | 61 days | 2027-01-14 |

## Which method predicts best? (fit on first days, test on last 7 days)

| Method | Mean absolute error (percentage points) |
|---|---|
| linear regression | 0.28 |
| baseline B: average daily change | 0.74 |
| baseline A: no growth (last value) | 2.02 |

Best on this held-out week: **linear regression**.

## Assumptions
- Growth stays roughly linear (steady daily increase); no new large application or data load.
- Readings are one per day at a similar time; no missing days.
- The ranges use 2 standard errors of the slope (about 95% if errors are roughly normal).

## Limitations
- A clean-up (like the log purge in the sample) lowers usage and makes a straight line less accurate.
- Only 30 days of fictional data; real usage has weekly cycles, releases and one-off jumps.
- The forecast says when the threshold is *likely* reached, not that it *will* be; re-run weekly.
- Disk % alone does not show *what* is growing; check `du` before acting (see Runbook 2).

## Operational takeaway
A static alert at 85% fires only when the disk is already nearly full. A trend alert such as 'less than 14 days to 85%' would warn earlier and avoid alerting on a disk that is high but not growing.