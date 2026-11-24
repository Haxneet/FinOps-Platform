"""Module 6: workload level -> required infrastructure -> monthly cost."""
from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd

from common.pricing import (
    ALB_HOURLY,
    ALB_LCU_HOURLY,
    DATA_TRANSFER_OUT_PER_GB,
    EC2_HOURLY,
    HOURS_PER_MONTH,
    RDS_HOURLY,
)

SECONDS_PER_MONTH = HOURS_PER_MONTH * 3600

# Default workload from the assignment (e-commerce, first half of the year)
DEFAULT_MONTHLY_REQUESTS = [
    ("January", 1_000_000),
    ("February", 2_000_000),
    ("March", 5_000_000),
    ("April", 8_000_000),
    ("May", 15_000_000),
    ("June", 25_000_000),
]

# Representative volumes for the low / medium / high comparison
DEFAULT_SCENARIOS = [
    ("Low", 2_000_000),
    ("Medium", 8_000_000),
    ("High", 15_000_000),
]

# (level name, minimum monthly requests), checked from the top down
LEVEL_THRESHOLDS = [
    ("Very high", 20_000_000),
    ("High", 10_000_000),
    ("Medium", 5_000_000),
    ("Low", 0),
]


@dataclass(frozen=True)
class WorkloadConfig:
    instance_type: str = "t3.medium"
    rps_per_instance: float = 8.0      # requests per second one instance can serve
    peak_factor: float = 5.0           # peak requests per second vs monthly average
    min_instances: int = 2             # kept for availability
    avg_response_kb: float = 150.0     # data returned per request
    include_rds: bool = True
    rds_type: str = "db.t3.medium"


def classify(monthly_requests: float) -> str:
    for name, floor in LEVEL_THRESHOLDS:
        if monthly_requests >= floor:
            return name
    return "Low"


def required_instances(monthly_requests: float, cfg: WorkloadConfig) -> int:
    avg_rps = monthly_requests / SECONDS_PER_MONTH
    peak_rps = avg_rps * cfg.peak_factor
    return max(cfg.min_instances, math.ceil(peak_rps / cfg.rps_per_instance))


def monthly_cost(monthly_requests: float, cfg: WorkloadConfig) -> dict:
    instances = required_instances(monthly_requests, cfg)
    ec2 = instances * EC2_HOURLY[cfg.instance_type] * HOURS_PER_MONTH

    gb_out = monthly_requests * cfg.avg_response_kb / 1_000_000
    avg_rps = monthly_requests / SECONDS_PER_MONTH
    lcu = max(1.0, gb_out / HOURS_PER_MONTH, avg_rps / 25)
    alb = (ALB_HOURLY + lcu * ALB_LCU_HOURLY) * HOURS_PER_MONTH

    rds = RDS_HOURLY[cfg.rds_type] * HOURS_PER_MONTH if cfg.include_rds else 0.0
    transfer = gb_out * DATA_TRANSFER_OUT_PER_GB

    total = ec2 + alb + rds + transfer
    return {
        "instances": instances,
        "ec2": ec2,
        "alb": alb,
        "rds": rds,
        "transfer": transfer,
        "total": total,
    }


def simulate(rows: list[tuple[str, float]], cfg: WorkloadConfig) -> pd.DataFrame:
    """rows is a list of (label, monthly_requests)."""
    out = []
    for label, requests in rows:
        c = monthly_cost(requests, cfg)
        out.append(
            {
                "Period": label,
                "Monthly requests": requests,
                "Workload level": classify(requests),
                "EC2 instances": c["instances"],
                "EC2 cost": round(c["ec2"], 2),
                "Load balancer cost": round(c["alb"], 2),
                "Database cost": round(c["rds"], 2),
                "Data transfer cost": round(c["transfer"], 2),
                "Total monthly cost": round(c["total"], 2),
                "Cost per 1M requests": round(c["total"] / (requests / 1_000_000), 2)
                if requests > 0
                else 0.0,
            }
        )
    return pd.DataFrame(out)
