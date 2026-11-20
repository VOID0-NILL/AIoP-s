"""Day 8 - Rolling z-score anomaly detection on metrics, with evaluation + chart."""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WINDOW = 60       # minutes of history used as baseline
Z_LIMIT = 4.0     # how many std-devs counts as unusual
MIN_RUN = 3       # must stay unusual this many minutes in a row
METRICS = ["latency_ms", "error_rate_percent"]

def detect(df, window=WINDOW, z_limit=Z_LIMIT, min_run=MIN_RUN, metrics=METRICS):
    """Rolling z-score against a baseline of recent NORMAL points only.
    Unusual points are kept out of the baseline, so a long incident cannot
    teach the detector that 'broken' is normal (baseline contamination)."""
    from collections import deque
    out = df.copy()
    for m in metrics:
        vals = out[m].to_numpy(dtype=float)
        base = deque(maxlen=window)
        z = [float("nan")] * len(vals)
        raw = [False] * len(vals)
        for i, v in enumerate(vals):
            if v != v:                      # missing value (NaN): skip, never learn from it
                continue
            if len(base) >= window // 2:
                mean = sum(base) / len(base)
                std = (sum((b - mean) ** 2 for b in base) / (len(base) - 1)) ** 0.5
                z[i] = (v - mean) / max(std, 1e-6)
                raw[i] = z[i] > z_limit
            if not raw[i]:
                base.append(v)
        # keep only runs of >= min_run consecutive unusual points (cuts one-off spikes)
        flag = [False] * len(vals)
        i = 0
        while i < len(vals):
            if raw[i]:
                j = i
                while j < len(vals) and raw[j]:
                    j += 1
                if j - i >= min_run:
                    for k in range(i, j):
                        flag[k] = True
                i = j
            else:
                i += 1
        out[f"{m}_z"] = z
        out[f"{m}_flag"] = flag
    out["anomaly"] = out[[f"{m}_flag" for m in metrics]].any(axis=1)
    return out

def evaluate(df, labels):
    truth = pd.Series(False, index=df.index)
    for _, r in labels.iterrows():
        truth |= (df["timestamp"] >= pd.to_datetime(r["start"])) & (df["timestamp"] < pd.to_datetime(r["end"]))
    pred = df["anomaly"]
    tp = int((pred & truth).sum()); fp = int((pred & ~truth).sum()); fn = int((~pred & truth).sum())
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": round(prec, 3), "recall": round(rec, 3)}

def plot(df, path="charts/anomalies.png"):
    fig, axes = plt.subplots(len(METRICS), 1, figsize=(11, 6), sharex=True)
    for ax, m in zip(axes, METRICS):
        ax.plot(df["timestamp"], df[m], lw=0.8, label=m)
        pts = df[df[f"{m}_flag"]]
        ax.scatter(pts["timestamp"], pts[m], color="red", s=10, label="flagged", zorder=3)
        ax.set_ylabel(m); ax.legend(loc="upper left")
    axes[-1].set_xlabel("Time")
    fig.suptitle("Anomaly detection (rolling z-score)"); fig.tight_layout()
    fig.savefig(path, dpi=120); plt.close(fig)

if __name__ == "__main__":
    metrics = pd.read_csv("metrics/metrics.csv", parse_dates=["timestamp"])
    labels = pd.read_csv("labels/incident_labels.csv")
    res = detect(metrics)
    res.to_csv("metrics/metrics_with_anomalies.csv", index=False)
    plot(res)
    print("Flagged minutes:", int(res["anomaly"].sum()))
    print("Evaluation vs ground truth:", evaluate(res, labels))
