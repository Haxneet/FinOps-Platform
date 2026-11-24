import pandas as pd

from logic import scaling, storage, workload


# ---- Module 6 ----
def test_classify_matches_assignment_levels():
    expected = {
        1_000_000: "Low",
        2_000_000: "Low",
        5_000_000: "Medium",
        8_000_000: "Medium",
        15_000_000: "High",
        25_000_000: "Very high",
    }
    for requests, level in expected.items():
        assert workload.classify(requests) == level


def test_instances_grow_with_requests_and_respect_minimum():
    cfg = workload.WorkloadConfig()
    counts = [workload.required_instances(r, cfg) for _, r in workload.DEFAULT_MONTHLY_REQUESTS]
    assert counts == sorted(counts)
    assert counts[0] == cfg.min_instances
    assert counts[-1] > counts[0]


def test_cost_increases_with_workload():
    cfg = workload.WorkloadConfig()
    df = workload.simulate(workload.DEFAULT_MONTHLY_REQUESTS, cfg)
    assert df["Total monthly cost"].is_monotonic_increasing
    row = df.iloc[0]
    parts = row["EC2 cost"] + row["Load balancer cost"] + row["Database cost"] + row["Data transfer cost"]
    assert abs(parts - row["Total monthly cost"]) < 0.05


def test_ec2_cost_for_minimum_fleet():
    cfg = workload.WorkloadConfig(include_rds=False)
    c = workload.monthly_cost(1_000_000, cfg)
    assert c["instances"] == 2
    assert round(c["ec2"], 2) == round(2 * 0.0416 * 730, 2)
    assert c["rds"] == 0


# ---- Module 12 ----
def _compare(fixed=8, min_i=2, max_i=8, overhead=10.0):
    return scaling.compare(
        "t3.medium", fixed, min_i, max_i,
        scaling.DEFAULT_REQUIRED, scaling.DEFAULT_SHARE_PCT, overhead, 5.0,
    )


def test_default_shares_total_100():
    assert sum(scaling.DEFAULT_SHARE_PCT.values()) == 100


def test_auto_scaling_cheaper_than_fixed_at_peak():
    r = _compare(fixed=8)
    assert r["auto_monthly"] < r["fixed_monthly"]
    assert r["savings_monthly"] > 0
    assert r["fixed_under_capacity_pct"] == 0


def test_fixed_below_peak_is_flagged_under_capacity():
    r = _compare(fixed=5)
    assert r["fixed_under_capacity_pct"] == scaling.DEFAULT_SHARE_PCT["Very high"]


def test_fixed_ec2_cost_matches_hand_calculation():
    r = _compare(fixed=3)
    expected_ec2 = 3 * 0.0416 * 730
    assert abs(r["table"]["Fixed EC2 cost"].sum() - expected_ec2) < 0.1


def test_max_instances_cap_is_flagged():
    r = _compare(fixed=8, max_i=6)
    very_high = r["table"].set_index("Workload level").loc["Very high"]
    assert very_high["Auto scaling running"] == 6
    assert very_high["Auto scaling status"] == "Capped at max"


def test_peak_share_sweep_shape():
    df = scaling.peak_share_sweep(
        "t3.medium", 8, 2, 8, scaling.DEFAULT_REQUIRED, scaling.DEFAULT_SHARE_PCT,
        10.0, 5.0, [0, 10, 20],
    )
    assert len(df) == 3
    assert df["Auto scaling"].is_monotonic_increasing


# ---- Module 13 ----
def _dataset():
    return pd.DataFrame(
        [(n, gb, p, "Standard") for n, gb, p in storage.DEFAULT_DATASET],
        columns=["Category", "Size (GB)", "Access pattern", "Current class"],
    )


def test_frequent_data_stays_in_standard():
    out = storage.analyze(_dataset()).set_index("Category")
    assert out.loc["Application files", "Recommended class"] == "Standard"
    assert out.loc["Application files", "Monthly savings"] == 0


def test_rare_data_moves_to_cheaper_class_and_saves_money():
    out = storage.analyze(_dataset()).set_index("Category")
    assert out.loc["Old logs", "Recommended class"] != "Standard"
    assert out.loc["Old logs", "Monthly savings"] > 0
    assert (out["Monthly savings"] >= 0).all()


def test_standard_cost_hand_calculation():
    out = storage.analyze(_dataset()).set_index("Category")
    assert out.loc["Application files", "Current monthly cost"] == round(200 * 0.023, 2)


def test_lifecycle_policy_saves_money_over_time():
    df = storage.lifecycle_simulation(
        monthly_ingest_gb=100, months=12, ia_after_days=30, archive_after_days=90,
        archive_class="Glacier Flexible Retrieval", expire_after_days=None,
        monthly_read_pct_of_archived=2.0,
    )
    assert df.iloc[0]["Monthly savings"] == 0
    assert df.iloc[-1]["Monthly savings"] > 0
    assert df.iloc[-1]["With policy cost"] < df.iloc[-1]["No policy cost"]


def test_lifecycle_expiry_limits_stored_data():
    df = storage.lifecycle_simulation(
        monthly_ingest_gb=100, months=12, ia_after_days=30, archive_after_days=90,
        archive_class="Glacier Flexible Retrieval", expire_after_days=180,
        monthly_read_pct_of_archived=2.0,
    )
    assert df.iloc[-1]["With policy (GB)"] < df.iloc[-1]["No policy (GB)"]


def test_longer_backup_retention_costs_more():
    df = storage.backup_retention(400, 3.0, [7, 30, 90], 90, None)
    assert df["Monthly cost"].is_monotonic_increasing
    row90 = df[df["Retention (days)"] == 90].iloc[0]
    assert row90["Savings vs current"] == 0
    assert df[df["Retention (days)"] == 7].iloc[0]["Savings vs current"] > 0


def test_cold_tiering_reduces_backup_cost():
    warm_only = storage.backup_retention(400, 3.0, [90], 90, None).iloc[0]["Monthly cost"]
    tiered = storage.backup_retention(400, 3.0, [90], 90, 30).iloc[0]["Monthly cost"]
    assert tiered < warm_only
