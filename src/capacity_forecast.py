"""Day 15 - Capacity & trend analysis: when will disk usage reach a threshold?
Compares a linear trend with two simple baselines on a held-out week, and reports uncertainty.

Input : metrics/disk_daily.csv  (columns: date, disk_percent). If missing, a fictional 30-day
        sample is created. To use REAL data, append one `df -h /` reading per day to that file.
Output: reports/capacity_report.md, charts/capacity_forecast.png
Run   : python3 src/capacity_forecast.py"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PATH = "metrics/disk_daily.csv"
WARN, CRIT = 85.0, 90.0
HOLDOUT = 7          # last 7 days are hidden while fitting, then used to test each method

def make_sample(path=PATH, days=30, seed=7):
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end="2026-11-20", periods=days)
    y = 62.0 + 0.45 * np.arange(days) + rng.normal(0, 0.25, days)   # about +0.45 % per day
    y[18:] -= 2.5                                                    # a log clean-up on day 19
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pd.DataFrame({"date": dates.date, "disk_percent": y.round(2)}).to_csv(path, index=False)

def linear_fit(x, y):
    slope, icpt = np.polyfit(x, y, 1)
    resid = y - (slope * x + icpt)
    s = resid.std(ddof=2)
    se_slope = s / np.sqrt(((x - x.mean()) ** 2).sum())
    return slope, icpt, s, se_slope

def days_to(threshold, level_now, rate):
    return float("inf") if rate <= 0 else max(0.0, (threshold - level_now) / rate)

def holdout_test(x, y, k=HOLDOUT):
    xt, yt, xh, yh = x[:-k], y[:-k], x[-k:], y[-k:]
    slope, icpt, _, _ = linear_fit(xt, yt)
    lin = slope * xh + icpt
    persist = np.full(k, yt[-1])                                  # baseline A: "no growth"
    avg_chg = yt[-1] + (yt[-1] - yt[0]) / (len(yt) - 1) * (xh - xt[-1])   # baseline B: average daily change
    mae = lambda p: float(np.mean(np.abs(p - yh)))
    return {"linear regression": mae(lin), "baseline A: no growth (last value)": mae(persist),
            "baseline B: average daily change": mae(avg_chg)}

def main():
    if not os.path.exists(PATH): make_sample()
    df = pd.read_csv(PATH, parse_dates=["date"]).dropna().sort_values("date").reset_index(drop=True)
    if len(df) < 14:
        print("Need at least 14 daily readings for a meaningful trend."); return
    x = (df["date"] - df["date"].iloc[0]).dt.days.to_numpy(float); y = df["disk_percent"].to_numpy(float)
    slope, icpt, s, se = linear_fit(x, y)
    now = slope * x[-1] + icpt
    rows = []
    for name, thr in (("warning 85%", WARN), ("critical 90%", CRIT)):
        mid = days_to(thr, now, slope)
        fast = days_to(thr, now, slope + 2 * se); slow = days_to(thr, now, slope - 2 * se)
        rows.append((name, mid, fast, slow, df["date"].iloc[-1] + pd.Timedelta(days=mid) if np.isfinite(mid) else None))
    errs = holdout_test(x, y)
    best = min(errs, key=errs.get)

    L = ["# Capacity forecast - disk usage", "",
         f"- Data: {len(df)} daily readings, {df['date'].min().date()} to {df['date'].max().date()} (fictional sample unless you replaced it with real readings)",
         f"- Latest reading: **{y[-1]:.1f}%**; trend-line level today: {now:.1f}%",
         f"- Linear trend: **{slope:+.2f} percentage points per day** (approx. range {slope - 2*se:+.2f} to {slope + 2*se:+.2f})", "",
         "## When will the threshold be reached? (from today)", "",
         "| Threshold | Best estimate | Fast case | Slow case | Estimated date |", "|---|---|---|---|---|"]
    fmt = lambda d: "never (trend flat)" if not np.isfinite(d) else f"{d:.0f} days"
    for name, mid, fast, slow, dt in rows:
        L.append(f"| {name} | {fmt(mid)} | {fmt(fast)} | {fmt(slow)} | {dt.date() if dt is not None else '-'} |")
    L += ["", "## Which method predicts best? (fit on first days, test on last 7 days)", "",
          "| Method | Mean absolute error (percentage points) |", "|---|---|"]
    for k, v in sorted(errs.items(), key=lambda kv: kv[1]):
        L.append(f"| {k} | {v:.2f} |")
    L += ["", f"Best on this held-out week: **{best}**.", "",
          "## Assumptions",
          "- Growth stays roughly linear (steady daily increase); no new large application or data load.",
          "- Readings are one per day at a similar time; no missing days.",
          "- The ranges use 2 standard errors of the slope (about 95% if errors are roughly normal).", "",
          "## Limitations",
          "- A clean-up (like the log purge in the sample) lowers usage and makes a straight line less accurate.",
          "- Only 30 days of fictional data; real usage has weekly cycles, releases and one-off jumps.",
          "- The forecast says when the threshold is *likely* reached, not that it *will* be; re-run weekly.",
          "- Disk % alone does not show *what* is growing; check `du` before acting (see Runbook 2).", "",
          "## Operational takeaway",
          "A static alert at 85% fires only when the disk is already nearly full. A trend alert such as "
          "'less than 14 days to 85%' would warn earlier and avoid alerting on a disk that is high but not growing."]
    open("reports/capacity_report.md", "w").write("\n".join(L)); print("\n".join(L))

    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(df["date"], y, "o", ms=4, color="#1b2a49", label="daily reading")
    horizon = int(min(120, max(30, (rows[1][2] if np.isfinite(rows[1][2]) else 60) * 1.5)))
    fx = np.arange(0, x[-1] + horizon + 1); fd = df["date"].iloc[0] + pd.to_timedelta(fx, unit="D")
    ax.plot(fd, slope * fx + icpt, color="#0e7c86", lw=2, label=f"linear trend ({slope:+.2f} pts/day)")
    ahead = np.clip(fx - x[-1], 0, None)               # days after the last reading
    ax.fill_between(fd, now + (slope - 2 * se) * ahead, now + (slope + 2 * se) * ahead,
                    where=fx >= x[-1], color="#0e7c86", alpha=0.18, label="uncertainty band (fast / slow case)")
    ax.axhline(y[-1], color="#888", ls=":", lw=1.2, label="baseline A: no growth")
    ax.axhline(WARN, color="#f2b134", ls="--", label="warning 85%"); ax.axhline(CRIT, color="#c0392b", ls="--", label="critical 90%")
    ax.set_ylim(min(y) - 2, 100); ax.set_ylabel("Disk usage (% of capacity)"); ax.set_xlabel("Date")
    ax.set_title("Disk usage trend and forecast (fictional sample data)", fontweight="bold")
    ax.grid(alpha=0.25); ax.legend(loc="upper left", fontsize=9); fig.tight_layout()
    os.makedirs("charts", exist_ok=True); fig.savefig("charts/capacity_forecast.png", dpi=110); plt.close(fig)
    print("\nSaved reports/capacity_report.md and charts/capacity_forecast.png")

if __name__ == "__main__":
    main()
