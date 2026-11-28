
"""Infrastructure configuration and validation for Module 3."""
import json
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

from common.data import HOURS_PER_MONTH
from common.pricing import EC2_HOURLY, RDS_HOURLY, S3_CLASSES


SUPPORTED_SERVICES = ["EC2", "S3", "DynamoDB", "Lambda", "RDS"]

REGIONS = [
    "us-east-1",
    "us-west-2",
    "ca-central-1",
]

EC2_INSTANCE_TYPES = list(EC2_HOURLY.keys())
RDS_INSTANCE_TYPES = list(RDS_HOURLY.keys())
S3_STORAGE_CLASSES = list(S3_CLASSES.keys())


def validate_scenario(name, region, resources):
    """Return validation errors for an infrastructure scenario."""

    errors = []

    if not name.strip():
        errors.append("Scenario name is required.")

    if region not in REGIONS:
        errors.append("Please select a valid region.")

    if not resources:
        errors.append("Select at least one cloud service.")

    for service, config in resources.items():

        if service not in SUPPORTED_SERVICES:
            errors.append(f"Unsupported service: {service}")
            continue

        for field, value in config.items():
            if isinstance(value, (int, float)) and value < 0:
                errors.append(
                    f"{service}: {field} cannot be negative."
                )

        if service in ["EC2", "RDS"]:
            if config.get("instance_count", 0) < 1:
                errors.append(
                    f"{service}: At least one instance is required."
                )

            hours = config.get("monthly_hours", 0)

            if not 0 < hours <= HOURS_PER_MONTH:
                errors.append(
                    f"{service}: Monthly hours must be between "
                    f"1 and {HOURS_PER_MONTH}."
                )
                    # Service-specific validation
    for service, config in resources.items():

        if service == "EC2":
            if config.get("instance_type") not in EC2_INSTANCE_TYPES:
                errors.append("EC2: Invalid instance type.")

            if config.get("operating_system", "Linux") not in [
                "Linux", "Windows"
            ]:
                errors.append("EC2: Invalid operating system.")

        elif service == "S3":
            if config.get("storage_class") not in S3_STORAGE_CLASSES:
                errors.append("S3: Invalid storage class.")

        elif service == "Lambda":
            if not 128 <= config.get("memory_mb", 0) <= 10240:
                errors.append("Lambda: Invalid memory allocation.")

            if not 1 <= config.get("duration_ms", 0) <= 900000:
                errors.append("Lambda: Invalid execution duration.")

        elif service == "RDS":
            if config.get("instance_type") not in RDS_INSTANCE_TYPES:
                errors.append("RDS: Invalid instance type.")

            if config.get("database_engine") not in [
                "MySQL", "PostgreSQL"
            ]:
                errors.append("RDS: Invalid database engine.")

    return errors


def create_scenario(name, region, resources):
    """Create a validated infrastructure scenario."""

    errors = validate_scenario(name, region, resources)

    if errors:
        raise ValueError("; ".join(errors))

    return {
        "id": str(uuid4()),
        "name": name.strip(),
        "region": region,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "resources": resources,
    }


SCENARIO_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "scenarios"
    / "infrastructure_scenarios.json"
)


def load_scenarios():
    """Load all previously saved infrastructure scenarios."""

    if not SCENARIO_FILE.exists():
        return []

    with SCENARIO_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_scenario(scenario):
    """Save a new infrastructure scenario."""

    scenarios = load_scenarios()
    scenarios.append(scenario)

    SCENARIO_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with SCENARIO_FILE.open("w", encoding="utf-8") as file:
        json.dump(scenarios, file, indent=4)

    return scenario



def delete_scenario(scenario_id):
    """Delete a saved scenario using its unique ID."""

    scenarios = load_scenarios()

    remaining = [
        scenario
        for scenario in scenarios
        if scenario["id"] != scenario_id
    ]

    if len(remaining) == len(scenarios):
        return False

    with SCENARIO_FILE.open("w", encoding="utf-8") as file:
        json.dump(remaining, file, indent=4)

    return True