"""Day 1 - Draws the College Portal data-flow diagram -> day01-foundations/dataflow.png
Run from the project root:  python3 src/make_diagram.py"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(13, 7.5)); ax.set_xlim(0, 13); ax.set_ylim(0, 7.5); ax.axis("off")

def box(x, y, w, h, title, sub, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.12",
                                fc=color, ec="#1b2a49", lw=1.4))
    ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="center", fontsize=10.5, fontweight="bold", color="#1b2a49")
    ax.text(x + w / 2, y + h / 2 - 0.2, sub, ha="center", va="center", fontsize=8.3, color="#333")

def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color="#1b2a49", lw=1.6))

ax.text(6.5, 7.15, "College Portal - AIOps data flow", ha="center", fontsize=15, fontweight="bold", color="#1b2a49")

# source system
box(0.3, 4.3, 2.6, 2.3, "COLLEGE PORTAL", "Web server\nApp server\nLogin service\nFee service\nDatabase", "#DCEBFA")
# three signal types
box(3.7, 5.6, 2.4, 0.95, "Logs", "logs/portal.log", "#FFF1CC")
box(3.7, 4.45, 2.4, 0.95, "Metrics", "metrics/metrics.csv", "#FFF1CC")
box(3.7, 3.3, 2.4, 0.95, "Events", "events/events.csv", "#FFF1CC")
for yy in (6.07, 4.92, 3.77): arrow(2.95, 5.45, 3.65, yy)
# processing
box(6.9, 4.9, 2.6, 1.5, "1. PARSE", "parse_logs.py\nstructured table", "#DFF2E3")
box(6.9, 3.0, 2.6, 1.5, "2. DETECT", "detect_anomalies.py\nrolling z-score", "#DFF2E3")
arrow(6.15, 6.07, 6.85, 5.8); arrow(6.15, 4.92, 6.85, 3.9)
arrow(8.2, 4.85, 8.2, 4.55)
# alert
box(10.2, 4.9, 2.5, 1.5, "3. ALERT", "alerts.py\nrules, severity,\nrouting, dedup", "#FCE0D2")
arrow(9.55, 3.75, 10.6, 4.85)
# correlate + report
box(10.2, 2.9, 2.5, 1.5, "4. CORRELATE", "incident_report.py\ntimeline +\nranked causes", "#E8E0F5")
arrow(11.45, 4.85, 11.45, 4.45)
# events go to CORRELATE along a path under DETECT (so it does not cross other boxes)
ax.plot([4.9, 4.9, 10.05, 10.05], [3.25, 2.6, 2.6, 3.1], color="#1b2a49", lw=1.6)
arrow(10.05, 3.1, 10.17, 3.1)
# outputs
box(6.9, 0.7, 2.6, 1.4, "REPORTS", "incident_report.md\ncorrelated_timeline.csv\ncharts/dashboard.png", "#D5F0F0")
box(10.2, 0.7, 2.5, 1.4, "HUMAN", "On-call engineer reads\nreport, approves any\naction (runbooks)", "#FBE4A8")
arrow(11.45, 2.85, 11.45, 2.15); arrow(10.4, 2.88, 9.55, 1.95); arrow(10.15, 1.4, 9.55, 1.4)
ax.text(0.3, 0.2, "Everything is synthetic data. The pipeline never changes a system: remediation stays human-approved.",
        fontsize=9, color="#555", style="italic")
os.makedirs("day01-foundations", exist_ok=True)
fig.savefig("day01-foundations/dataflow.png", dpi=110, bbox_inches="tight"); print("Saved day01-foundations/dataflow.png")
