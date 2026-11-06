"""Shared AWS client factory pointed at the Floci endpoint."""
import os

import boto3
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = os.getenv("FLOCI_ENDPOINT", "http://localhost:4566")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")


def client(service: str, region: str | None = None):
    """Return a boto3 client for `service` using the Floci endpoint.

    Example: client("pricing"), client("ce"), client("budgets"), client("cloudwatch")
    """
    return boto3.client(
        service,
        endpoint_url=ENDPOINT,
        region_name=region or REGION,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
    )
