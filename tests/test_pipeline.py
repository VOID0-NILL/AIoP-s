"""Run from the project root:  python3 -m unittest discover -s tests -v"""
import os, sys, unittest
import numpy as np, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src")); os.chdir(ROOT)
from parse_logs import parse_line
from detect_anomalies import detect, evaluate
from alerts import evaluate_rules, group_alerts
from health_check import check_row, main as health_main

def load():
    m = pd.read_csv("metrics/metrics.csv", parse_dates=["timestamp"])
    return m, pd.read_csv("labels/incident_labels.csv")

class TestParser(unittest.TestCase):
    def test_valid_line(self):
        r = parse_line("2026-11-20 14:06:11,119 | ERROR | fee-service | database | Connection pool exhausted (max=20)")
        self.assertEqual((r["level"], r["service"], r["component"]), ("ERROR", "fee-service", "database"))
    def test_malformed_line_returns_none(self):
        self.assertIsNone(parse_line("garbage without fields"))
        self.assertIsNone(parse_line(""))

class TestDetection(unittest.TestCase):
    def setUp(self): self.m, self.labels = load()
    def test_normal_data_has_no_anomalies(self):
        normal = self.m[self.m["timestamp"] < "2026-11-20 14:00:00"].reset_index(drop=True)
        self.assertEqual(int(detect(normal)["anomaly"].sum()), 0)
    def test_incident_is_detected(self):
        res = evaluate(detect(self.m), self.labels)
        self.assertGreaterEqual(res["recall"], 0.9); self.assertGreaterEqual(res["precision"], 0.9)
    def test_missing_values_do_not_crash(self):
        bad = self.m.copy(); bad.loc[100:110, "latency_ms"] = np.nan
        res = evaluate(detect(bad), self.labels)
        self.assertGreaterEqual(res["recall"], 0.9)
    def test_single_spike_is_not_flagged(self):
        spike = self.m[self.m["timestamp"] < "2026-11-20 14:00:00"].reset_index(drop=True)
        spike.loc[300, "latency_ms"] = 5000
        self.assertEqual(int(detect(spike)["anomaly"].sum()), 0)
    def test_noisy_data_reports_metrics(self):
        rng = np.random.default_rng(1); noisy = self.m.copy()
        noisy["latency_ms"] += rng.normal(0, 60, len(noisy))      # 6x the original noise
        res = evaluate(detect(noisy), self.labels)
        print("\n  [noisy-data result]", res)                       # recorded for the Day 19 results table
        self.assertGreaterEqual(res["recall"], 0.8)

class TestAlerts(unittest.TestCase):
    def setUp(self): self.m, _ = load()
    def test_no_alerts_on_normal_day_part(self):
        normal = self.m[self.m["timestamp"] < "2026-11-20 14:00:00"]
        self.assertEqual(len(evaluate_rules(normal)), 0)
    def test_incident_fires_and_groups_into_one(self):
        a = group_alerts(evaluate_rules(self.m))
        self.assertGreaterEqual(len(a), 2); self.assertEqual(a["group_id"].nunique(), 1)
    def test_short_breach_does_not_fire(self):
        d = self.m[self.m["timestamp"] < "2026-11-20 14:00:00"].copy().reset_index(drop=True)
        d.loc[200:201, "latency_ms"] = 3000                          # only 2 minutes < 3 required
        self.assertEqual(len(evaluate_rules(d)), 0)

class TestHealthCheck(unittest.TestCase):
    def test_exit_codes(self):
        ok = dict(cpu_percent=30, memory_percent=50, disk_percent=50, latency_ms=100, error_rate_percent=0.1)
        self.assertEqual(check_row(ok)[0], 0)
        self.assertEqual(check_row({**ok, "cpu_percent": 75})[0], 1)
        self.assertEqual(check_row({**ok, "latency_ms": 1500})[0], 2)
        self.assertEqual(check_row({**ok, "disk_percent": None})[0], 1)
    def test_missing_file_returns_3(self):
        self.assertEqual(health_main(["--metrics", "does_not_exist.csv"]), 3)

if __name__ == "__main__":
    unittest.main()
