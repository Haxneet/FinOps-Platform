"""Module 13: storage class, lifecycle and backup retention cost analysis."""
from __future__ import annotations

import pandas as pd

from common.pricing import BACKUP_COLD_PER_GB, BACKUP_WARM_PER_GB, S3_CLASSES

# Assignment dataset
DEFAULT_DATASET = [
    ("Application files", 200, "Frequent"),
    ("Current reports", 100, "Frequent"),
    ("Historical reports", 500, "Infrequent"),
    ("Old logs", 300, "Rare"),
    ("Database backups", 400, "Periodic"),
]

# Assumed share of the data read back each month, by access pattern
RETRIEVED_FRACTION = {
    "Frequent": 1.0,
    "Periodic": 0.20,
    "Infrequent": 0.05,
    "Rare": 0.01,
}

# Storage classes that are sensible for each access pattern
ALLOWED_CLASSES = {
    "Frequent": ["Standard"],
    "Periodic": ["Standard", "Standard-IA"],
    "Infrequent": ["Standard", "Standard-IA", "Glacier Instant Retrieval"],
    "Rare": [
        "Standard",
        "Standard-IA",
        "Glacier Instant Retrieval",
        "Glacier Flexible Retrieval",
        "Deep Archive",
    ],
}


def class_cost(gb: float, storage_class: str, retrieved_fraction: float) -> float:
    p = S3_CLASSES[storage_class]
    return gb * p["storage"] + gb * retrieved_fraction * p["retrieval"]


def analyze(df: pd.DataFrame) -> pd.DataFrame:
    """df columns: Category, Size (GB), Access pattern, Current class."""
    rows = []
    for _, r in df.iterrows():
        gb = float(r["Size (GB)"])
        pattern = r["Access pattern"]
        frac = RETRIEVED_FRACTION[pattern]
        current = class_cost(gb, r["Current class"], frac)
        best_class, best_cost = min(
            ((c, class_cost(gb, c, frac)) for c in ALLOWED_CLASSES[pattern]),
            key=lambda x: x[1],
        )
        rows.append(
            {
                "Category": r["Category"],
                "Size (GB)": gb,
                "Access pattern": pattern,
                "Current class": r["Current class"],
                "Current monthly cost": round(current, 2),
                "Recommended class": best_class,
                "Recommended monthly cost": round(best_cost, 2),
                "Monthly savings": round(current - best_cost, 2),
                "Retrieval time": S3_CLASSES[best_class]["retrieval_time"],
            }
        )
    return pd.DataFrame(rows)


def lifecycle_simulation(
    monthly_ingest_gb: float,
    months: int,
    ia_after_days: int,
    archive_after_days: int,
    archive_class: str,
    expire_after_days: int | None,
    monthly_read_pct_of_archived: float,
) -> pd.DataFrame:
    """Compare keeping everything in Standard with a lifecycle policy.

    Each month a new batch of data arrives. A batch that is N months old is
    treated as N * 30 days old. Transition request fees and minimum storage
    duration charges are not modelled.
    """
    std = S3_CLASSES["Standard"]
    ia = S3_CLASSES["Standard-IA"]
    arc = S3_CLASSES[archive_class]
    read_frac = monthly_read_pct_of_archived / 100

    rows = []
    for t in range(1, months + 1):
        no_policy_gb = monthly_ingest_gb * t
        no_policy_cost = no_policy_gb * std["storage"]

        gb_std = gb_ia = gb_arc = 0.0
        for m in range(1, t + 1):
            age_days = (t - m) * 30
            if expire_after_days is not None and age_days >= expire_after_days:
                continue
            if age_days >= archive_after_days:
                gb_arc += monthly_ingest_gb
            elif age_days >= ia_after_days:
                gb_ia += monthly_ingest_gb
            else:
                gb_std += monthly_ingest_gb

        policy_cost = (
            gb_std * std["storage"]
            + gb_ia * (ia["storage"] + read_frac * ia["retrieval"])
            + gb_arc * (arc["storage"] + read_frac * arc["retrieval"])
        )
        rows.append(
            {
                "Month": t,
                "No policy (GB)": no_policy_gb,
                "With policy (GB)": gb_std + gb_ia + gb_arc,
                "No policy cost": round(no_policy_cost, 2),
                "With policy cost": round(policy_cost, 2),
                "Monthly savings": round(no_policy_cost - policy_cost, 2),
            }
        )
    return pd.DataFrame(rows)


def backup_retention(
    base_gb: float,
    daily_change_pct: float,
    retention_days_options: list[int],
    current_retention_days: int,
    cold_after_days: int | None,
) -> pd.DataFrame:
    """Cost of keeping backups for different retention periods.

    Incremental-forever model: one full copy plus the daily changed data for
    each retained day. If cold_after_days is set, changed data older than that
    moves to cold storage.
    """
    change_gb = base_gb * daily_change_pct / 100

    def cost(days: int) -> tuple[float, float, float]:
        if cold_after_days is None:
            warm = base_gb + change_gb * days
            cold = 0.0
        else:
            warm = base_gb + change_gb * min(days, cold_after_days)
            cold = change_gb * max(0, days - cold_after_days)
        return warm, cold, warm * BACKUP_WARM_PER_GB + cold * BACKUP_COLD_PER_GB

    current_cost = cost(current_retention_days)[2]
    rows = []
    for d in retention_days_options:
        warm, cold, c = cost(d)
        rows.append(
            {
                "Retention (days)": d,
                "Warm storage (GB)": round(warm, 1),
                "Cold storage (GB)": round(cold, 1),
                "Monthly cost": round(c, 2),
                "Savings vs current": round(current_cost - c, 2),
            }
        )
    return pd.DataFrame(rows)
