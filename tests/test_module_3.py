
"""Automated tests for Module 3 - Infrastructure Builder."""

import pytest

from logic import infrastructure
from logic.infrastructure import (
    create_scenario,
    validate_scenario,
    save_scenario,
    load_scenarios,
    delete_scenario,
)


def sample_resources():
    return {
        "EC2": {
            "instance_type": "t3.small",
            "instance_count": 3,
            "monthly_hours": 730,
            "operating_system": "Linux",
            "storage_gb": 100,
        },
        "S3": {
            "storage_class": "Standard",
            "storage_gb": 500,
        },
    }


@pytest.fixture
def temporary_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(
        infrastructure,
        "SCENARIO_FILE",
        tmp_path / "scenarios.json",
    )


def test_valid_scenario():
    errors = validate_scenario(
        "Test Scenario", "us-east-1", sample_resources()
    )
    assert errors == []


def test_empty_name():
    errors = validate_scenario(
        "", "us-east-1", sample_resources()
    )
    assert "Scenario name is required." in errors


def test_invalid_region():
    errors = validate_scenario(
        "Test", "invalid-region", sample_resources()
    )
    assert "Please select a valid region." in errors


def test_no_services():
    errors = validate_scenario("Test", "us-east-1", {})
    assert "Select at least one cloud service." in errors


def test_negative_storage():
    resources = sample_resources()
    resources["S3"]["storage_gb"] = -100

    assert validate_scenario(
        "Test", "us-east-1", resources
    )


def test_invalid_instance_count():
    resources = sample_resources()
    resources["EC2"]["instance_count"] = 0

    assert validate_scenario(
        "Test", "us-east-1", resources
    )


def test_invalid_monthly_hours():
    resources = sample_resources()
    resources["EC2"]["monthly_hours"] = 800

    assert validate_scenario(
        "Test", "us-east-1", resources
    )


def test_invalid_instance_type():
    resources = sample_resources()
    resources["EC2"]["instance_type"] = "invalid"

    assert "EC2: Invalid instance type." in validate_scenario(
        "Test", "us-east-1", resources
    )


def test_invalid_s3_storage_class():
    resources = sample_resources()
    resources["S3"]["storage_class"] = "invalid"

    assert "S3: Invalid storage class." in validate_scenario(
        "Test", "us-east-1", resources
    )


def test_create_scenario():
    scenario = create_scenario(
        "Test", "us-east-1", sample_resources()
    )

    assert scenario["name"] == "Test"
    assert scenario["region"] == "us-east-1"
    assert "id" in scenario
    assert "created_at" in scenario
    assert len(scenario["resources"]) == 2


def test_create_invalid_scenario():
    with pytest.raises(ValueError):
        create_scenario("", "us-east-1", {})


def test_empty_storage(temporary_storage):
    assert load_scenarios() == []


def test_save_and_load(temporary_storage):
    scenario = create_scenario(
        "Test", "us-east-1", sample_resources()
    )

    save_scenario(scenario)

    assert load_scenarios() == [scenario]


def test_multiple_scenarios(temporary_storage):
    first = create_scenario(
        "Scenario One", "us-east-1", sample_resources()
    )
    second = create_scenario(
        "Scenario Two", "us-west-2", sample_resources()
    )

    save_scenario(first)
    save_scenario(second)

    assert len(load_scenarios()) == 2
    assert first["id"] != second["id"]


def test_delete_scenario(temporary_storage):
    scenario = create_scenario(
        "Delete Test", "us-east-1", sample_resources()
    )

    save_scenario(scenario)

    assert delete_scenario(scenario["id"]) is True
    assert load_scenarios() == []


def test_delete_nonexistent_scenario(temporary_storage):
    assert delete_scenario("invalid-id") is False
