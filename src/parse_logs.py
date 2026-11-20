"""Day 4/7 - Parse portal.log into a table and summarise errors."""
import re, sys
import pandas as pd

LINE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \| (?P<level>\w+)\s*\| "
    r"(?P<service>[\w-]+) \| (?P<component>[\w-]+) \| (?P<message>.*)$")

def parse_line(line):
    """Return a dict for a valid log line, or None for a malformed one."""
    m = LINE.match(line.strip())
    return m.groupdict() if m else None

def parse_file(path):
    rows, bad = [], 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.strip():
                continue
            rec = parse_line(line)
            if rec is None:
                bad += 1
            else:
                rows.append(rec)
    df = pd.DataFrame(rows)
    if df.empty:
        return df, bad
    df["timestamp"] = pd.to_datetime(df.pop("ts"), format="%Y-%m-%d %H:%M:%S,%f")
    # normalise variable parts so similar messages group together
    df["pattern"] = (df["message"]
                     .str.replace(r"user_id=\d+", "user_id=<ID>", regex=True)
                     .str.replace(r"/results/\d+", "/results/<ID>", regex=True)
                     .str.replace(r"\d+ms", "<N>ms", regex=True)
                     .str.replace(r"duration=\d+ms", "duration=<N>ms", regex=True))
    return df, bad

def summarise(df, bad):
    err = df[df["level"] == "ERROR"]
    out = ["# Log findings", "",
           f"- Records parsed: **{len(df)}** (malformed lines skipped: {bad})",
           f"- Time range: {df['timestamp'].min()} to {df['timestamp'].max()}",
           f"- Level counts: {df['level'].value_counts().to_dict()}", "",
           "## Errors by service", err["service"].value_counts().to_string(), "",
           "## Top 5 error patterns", err["pattern"].value_counts().head(5).to_string(), "",
           "## Errors per 10-minute window (top 6)",
           err.set_index("timestamp").resample("10min").size().sort_values(ascending=False).head(6).to_string(), "",
           "## Noisiest repeated messages (all levels, top 5)", df["pattern"].value_counts().head(5).to_string(), "",
           "## Limitations",
           "- Synthetic data: one injected incident, so patterns are cleaner than real logs.",
           "- Pattern grouping uses simple regex; unseen formats would stay ungrouped."]
    return "\n".join(out)

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "logs/portal.log"
    df, bad = parse_file(path)
    df.to_csv("logs/parsed_logs.csv", index=False)
    text = summarise(df, bad)
    open("reports/log_findings.md", "w").write(text)
    print(text)
