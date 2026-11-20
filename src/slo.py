"""Day 16 - SLI / SLO / error budget from the metrics file (fictional service)."""
import pandas as pd
SLO_TARGET = 99.5          # % of minutes that must be "good"
LATENCY_LIMIT_MS = 1000    # a minute is "bad" if latency is above this ...
ERROR_LIMIT_PCT = 5.0      # ... or error rate is above this

def compute(m):
    bad = (m["latency_ms"] > LATENCY_LIMIT_MS) | (m["error_rate_percent"] > ERROR_LIMIT_PCT)
    total = len(m); bad_n = int(bad.sum())
    sli = 100 * (total - bad_n) / total
    budget_min = total * (100 - SLO_TARGET) / 100
    return {"total_minutes": total, "bad_minutes": bad_n, "sli_percent": round(sli, 2),
            "slo_percent": SLO_TARGET, "error_budget_minutes": round(budget_min, 1),
            "budget_consumed_percent": round(100 * bad_n / budget_min, 1), "slo_met": sli >= SLO_TARGET}

if __name__ == "__main__":
    r = compute(pd.read_csv("metrics/metrics.csv", parse_dates=["timestamp"]))
    for k, v in r.items(): print(f"{k}: {v}")
    open("reports/slo_report.md", "w").write("# SLO report (24h, fictional data)\n\n" + "\n".join(f"- {k}: **{v}**" for k, v in r.items()) +
        f"\n\nSLI = share of minutes with latency <= {LATENCY_LIMIT_MS} ms AND error rate <= {ERROR_LIMIT_PCT}%.\n")
