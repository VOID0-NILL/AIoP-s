"""Day 14 - First-pass check of an AI-written summary against the source data.
Usage: put the AI's answer in reports/ai_summary.txt, then run:  python3 src/check_summary.py
It checks times, numbers with units, versions and service names. It CANNOT judge meaning,
causes or wording - you must still verify every other claim by hand in your validation table."""
import re, sys

SRC, SUM = "reports/ai_input.txt", "reports/ai_summary.txt"
PATTERNS = {
    "time":    r"\b\d{1,2}:\d{2}(?::\d{2})?\b",
    "number":  r"\b\d[\d,]*(?:\.\d+)?\s?(?:(?:ms|minutes?|min)\b|%)",
    "version": r"\bv\d+(?:\.\d+)+\b",
    "service": r"\b(?:[a-z]+-(?:service|server)|database)\b",
}
norm = lambda s: re.sub(r"\s+", " ", s.replace(",", "").lower()).strip()

def main():
    try:
        src, summ = open(SRC).read(), open(SUM).read()
    except FileNotFoundError as e:
        print("Missing file:", e.filename); return 1
    s_norm = norm(src)
    rows, bad = [], 0
    for kind, pat in PATTERNS.items():
        for tok in sorted(set(re.findall(pat, summ, flags=re.I))):
            t = norm(tok)
            if kind == "number":      # same number AND same unit, not just a matching substring
                num, unit = re.match(r"([\d.]+)\s?(\S+)", t).groups()
                found = bool(re.search(r"(?<![\d.])" + re.escape(num) + r"(?:\.0)?\s?" + re.escape(unit), s_norm))
            elif kind == "time":
                found = bool(re.search(r"(?<!\d)" + re.escape(t), s_norm))
            else:
                found = t in s_norm
            rows.append((kind, tok, "found in source" if found else "NOT FOUND - check"))
            bad += not found
    out = ["# AI summary - automatic first-pass check", "",
           "| Type | Item in AI summary | Result |", "|---|---|---|"]
    out += [f"| {k} | {t} | {r} |" for k, t, r in rows]
    out += ["", f"Items not found: **{bad}** of {len(rows)}.", "",
            "Reminder: this checks only times, numbers, versions and service names. "
            "Claims about causes, impact and recommendations must be verified by hand."]
    open("reports/ai_validation_draft.md", "w").write("\n".join(out)); print("\n".join(out))
    return 0

if __name__ == "__main__":
    sys.exit(main())
