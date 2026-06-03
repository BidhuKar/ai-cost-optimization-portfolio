"""Unit tests for synth_generator.py — run: pytest tests/ -v"""
import sys, math
from pathlib import Path
import pytest, numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "data" / "synthetic_generator"))
from synth_generator import (
    generate_billing_data, random_timestamp, pick_service_and_resource,
    compute_cost, SERVICES, TEAMS, REGIONS, ANOMALY_RATE,
)

@pytest.fixture(scope="module")
def small_df():
    return generate_billing_data(n_rows=500)

class TestSchema:
    COLS = {"record_id","timestamp","account_id","team","service","region",
            "resource_type","usage_hours","unit_cost","total_cost","anomaly_flag"}
    def test_columns(self, small_df):      assert self.COLS == set(small_df.columns)
    def test_no_nulls(self, small_df):     assert small_df.isnull().sum().sum() == 0
    def test_row_count(self, small_df):    assert len(small_df) == 500
    def test_unique_ids(self, small_df):   assert small_df["record_id"].nunique() == 500
    def test_anomaly_dtype(self, small_df):assert small_df["anomaly_flag"].dtype == bool

class TestDomain:
    def test_services(self, small_df): assert set(small_df["service"].unique()).issubset(SERVICES)
    def test_teams(self, small_df):    assert set(small_df["team"].unique()).issubset(TEAMS)
    def test_regions(self, small_df):  assert set(small_df["region"].unique()).issubset(REGIONS)
    def test_usage_positive(self, small_df):     assert (small_df["usage_hours"] > 0).all()
    def test_total_cost_positive(self, small_df):assert (small_df["total_cost"] > 0).all()
    def test_sorted_by_time(self, small_df):
        assert (small_df["timestamp"].diff().dropna() >= pd.Timedelta(0)).all()

class TestAnomalies:
    def test_rate_in_bounds(self, small_df):
        rate = small_df["anomaly_flag"].mean()
        assert 0.0 <= rate <= 0.15
    def test_anomaly_cost_higher(self, small_df):
        if small_df["anomaly_flag"].sum() > 5:
            assert (small_df.loc[small_df["anomaly_flag"],"total_cost"].mean() >
                    small_df.loc[~small_df["anomaly_flag"],"total_cost"].mean())

class TestHelpers:
    def test_timestamp_recent(self):
        from datetime import datetime, timezone, timedelta
        ts = random_timestamp(90)
        assert datetime.now(tz=timezone.utc) - timedelta(days=91) <= ts
    def test_service_resource_valid(self):
        svc, res = pick_service_and_resource()
        assert svc in SERVICES and res in SERVICES[svc]
    def test_normal_cost(self):
        unit, total = compute_cost("Compute", 10.0, False)
        assert unit > 0 and math.isclose(total, round(10.0 * unit, 4), rel_tol=1e-3)
    def test_anomaly_spike(self):
        normals  = [compute_cost("ML", 5.0, False)[1] for _ in range(50)]
        anomalies= [compute_cost("ML", 5.0, True)[1]  for _ in range(50)]
        assert np.mean(anomalies) > np.mean(normals)

def test_end_to_end(tmp_path):
    out = tmp_path / "test.csv"
    df = generate_billing_data(100)
    df.to_csv(out, index=False)
    loaded = pd.read_csv(out, parse_dates=["timestamp"])
    assert len(loaded) == 100 and loaded["total_cost"].sum() > 0
