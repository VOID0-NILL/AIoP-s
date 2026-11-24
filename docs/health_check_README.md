# health_check.py - run instructions (Day 3 and Day 12)

A safe, read-only check of one row of metrics against warning and critical thresholds.
It never changes anything on the system.

## Run (from the project root)
    python3 src/pipeline.py                      # creates metrics/metrics.csv if needed (or run src/generate_data.py)
    python3 src/health_check.py                  # checks the last row
    python3 src/health_check.py --at "2026-11-20 14:20:00"
    python3 src/health_check.py --at "2026-11-20 14:20:00" --report   # also writes reports/health_report_<timestamp>.txt

## Exit codes
| Code | Meaning |
|---|---|
| 0 | OK |
| 1 | WARNING (or a value missing) |
| 2 | CRITICAL |
| 3 | Could not run (file missing, time not found, bad input, report not writable) |

## Sample input
metrics/metrics.csv with columns: timestamp, cpu_percent, memory_percent, disk_percent, latency_ms, request_rate_per_min, error_rate_percent

## Sample output (during the incident, 14:20)
    Checked 2026-11-20 14:20:00
    cpu_percent=83.0 WARNING (>= 70)
    memory_percent=71.5 OK
    disk_percent=61.8 OK
    latency_ms=1905.0 CRITICAL (>= 1000)
    error_rate_percent=19.56 CRITICAL (>= 5)
    Result: CRITICAL            (exit code 2)

## Sample output (normal time, 10:00)
    All five indicators OK      (exit code 0)

## Tests
tests/test_pipeline.py covers exit codes 0, 1, 2 and 3, and a missing input file.
