"""Module 12: fixed infrastructure vs auto scaling cost."""
from __future__ import annotations

import pandas as pd

from common.pricing import ALB_HOURLY, ALB_LCU_HOURLY, EC2_HOURLY, HOURS_PER_MONTH

# From the assignment: instances needed at each workload level
DEFAULT_REQUIRED = {"Low": 2, "Medium": 3, "High": 5, "Very high": 8}

# Assumed share of the month spent at each level (must total 100)
DEFAULT_SHARE_PCT = {"Low": 40.0, "Medium": 35.0, "High": 20.0, "Very high": 5.0}

LEVELS = list(DEFAULT_REQUIRED.keys())


def alb_monthly(avg_lcu: float) -> float:
    return (ALB_HOURLY + avg_lcu * ALB_LCU_HOURLY) * HOURS_PER_MONTH


def level_table(
    instance_type: str,
    fixed_count: int,
    min_instances: int,
    max_instances: int,
    required: dict[str, int],
    share_pct: dict[str, float],
    scale_overhead_pct: float,
) -> pd.DataFrame:
    """Per workload level: what each approach runs and costs for the month."""
    price = EC2_HOURLY[instance_type]
    rows = []
    for level in LEVELS:
        hours = HOURS_PER_MONTH * share_pct[level] / 100
        need = required[level]
        auto_running = min(max(need, min_instances), max_instances)
        overhead = 1 + scale_overhead_pct / 100
        rows.append(
            {
                "Workload level": level,
                "Share of month (%)": share_pct[level],
                "Hours": round(hours, 1),
                "Instances required": need,
                "Fixed running": fixed_count,
                "Auto scaling running": auto_running,
                "Fixed EC2 cost": round(fixed_count * price * hours, 2),
                "Auto scaling EC2 cost": round(auto_running * price * hours * overhead, 2),
                "Fixed status": "Under capacity" if fixed_count < need else "OK",
                "Auto scaling status": "Capped at max" if need > max_instances else "OK",
            }
        )
    return pd.DataFrame(rows)


def compare(
    instance_type: str,
    fixed_count: int,
    min_instances: int,
    max_instances: int,
    required: dict[str, int],
    share_pct: dict[str, float],
    scale_overhead_pct: float,
    avg_lcu: float,
) -> dict:
    table = level_table(
        instance_type, fixed_count, min_instances, max_instances,
        required, share_pct, scale_overhead_pct,
    )
    alb = alb_monthly(avg_lcu)
    fixed_total = table["Fixed EC2 cost"].sum() + alb
    auto_total = table["Auto scaling EC2 cost"].sum() + alb
    savings = fixed_total - auto_total
    under_pct = float(
        table.loc[table["Fixed status"] == "Under capacity", "Share of month (%)"].sum()
    )
    return {
        "table": table,
        "alb_monthly": alb,
        "fixed_monthly": fixed_total,
        "auto_monthly": auto_total,
        "savings_monthly": savings,
        "savings_pct": (savings / fixed_total * 100) if fixed_total else 0.0,
        "savings_annual": savings * 12,
        "fixed_under_capacity_pct": under_pct,
    }


def fixed_strategies(
    required: dict[str, int], share_pct: dict[str, float]
) -> dict[str, int]:
    """Common ways to size a fixed fleet."""
    peak = max(required.values())
    weighted = sum(required[l] * share_pct[l] for l in LEVELS) / 100
    return {
        "Fixed at peak": peak,
        "Fixed at average (rounded up)": int(-(-weighted // 1)),
        "Fixed at median level": sorted(required.values())[len(required) // 2],
    }


def strategy_table(
    instance_type: str,
    min_instances: int,
    max_instances: int,
    required: dict[str, int],
    share_pct: dict[str, float],
    scale_overhead_pct: float,
    avg_lcu: float,
) -> pd.DataFrame:
    rows = []
    for name, count in fixed_strategies(required, share_pct).items():
        r = compare(
            instance_type, count, min_instances, max_instances,
            required, share_pct, scale_overhead_pct, avg_lcu,
        )
        rows.append(
            {
                "Fixed strategy": name,
                "Instances": count,
                "Fixed monthly cost": round(r["fixed_monthly"], 2),
                "Auto scaling monthly cost": round(r["auto_monthly"], 2),
                "Savings with auto scaling": round(r["savings_monthly"], 2),
                "Time under capacity (%)": r["fixed_under_capacity_pct"],
            }
        )
    return pd.DataFrame(rows)


def peak_share_sweep(
    instance_type: str,
    fixed_count: int,
    min_instances: int,
    max_instances: int,
    required: dict[str, int],
    share_pct: dict[str, float],
    scale_overhead_pct: float,
    avg_lcu: float,
    peak_shares: list[float],
) -> pd.DataFrame:
    """How the comparison changes as more of the month is spent at Very high."""
    others = [l for l in LEVELS if l != "Very high"]
    other_total = sum(share_pct[l] for l in others)
    rows = []
    for ps in peak_shares:
        shares = {l: share_pct[l] * (100 - ps) / other_total for l in others}
        shares["Very high"] = ps
        r = compare(
            instance_type, fixed_count, min_instances, max_instances,
            required, shares, scale_overhead_pct, avg_lcu,
        )
        rows.append(
            {
                "Very high share (%)": ps,
                "Fixed": round(r["fixed_monthly"], 2),
                "Auto scaling": round(r["auto_monthly"], 2),
            }
        )
    return pd.DataFrame(rows)
