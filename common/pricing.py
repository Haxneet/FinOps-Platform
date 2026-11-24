"""Documented price assumptions used by Modules 6, 12 and 13.

These are approximate AWS public list prices for us-east-1 (Linux, On-Demand).
They are NOT retrieved from the Floci Pricing API. When Module 1 (Pricing
Explorer) can supply real values, replace the numbers here in one place and
every page picks them up.
"""
from common.data import HOURS_PER_MONTH

REGION = "us-east-1"

PRICING_SOURCE = (
    "Documented assumptions based on approximate AWS public list prices "
    "(us-east-1, Linux, On-Demand). Not retrieved from the Floci Pricing API."
)

# EC2 On-Demand, USD per instance-hour
EC2_HOURLY = {
    "t3.small": 0.0208,
    "t3.medium": 0.0416,
    "t3.large": 0.0832,
    "m5.large": 0.096,
    "m5.xlarge": 0.192,
}

# RDS On-Demand, USD per instance-hour (single-AZ, MySQL/PostgreSQL class)
RDS_HOURLY = {
    "db.t3.medium": 0.068,
    "db.t3.large": 0.136,
}

# Application Load Balancer
ALB_HOURLY = 0.0225          # USD per hour
ALB_LCU_HOURLY = 0.008       # USD per LCU-hour

# Data transfer out to the internet, USD per GB (free tier ignored)
DATA_TRANSFER_OUT_PER_GB = 0.09

# S3 storage classes: USD per GB-month, retrieval USD per GB, typical retrieval time
S3_CLASSES = {
    "Standard": {"storage": 0.023, "retrieval": 0.0, "retrieval_time": "Immediate"},
    "Standard-IA": {"storage": 0.0125, "retrieval": 0.01, "retrieval_time": "Immediate"},
    "Glacier Instant Retrieval": {"storage": 0.004, "retrieval": 0.03, "retrieval_time": "Immediate"},
    "Glacier Flexible Retrieval": {"storage": 0.0036, "retrieval": 0.01, "retrieval_time": "Minutes to hours"},
    "Deep Archive": {"storage": 0.00099, "retrieval": 0.02, "retrieval_time": "Up to 12 hours"},
}

# AWS Backup, USD per GB-month
BACKUP_WARM_PER_GB = 0.05
BACKUP_COLD_PER_GB = 0.01


def ec2_hourly(instance_type: str) -> float:
    return EC2_HOURLY[instance_type]
