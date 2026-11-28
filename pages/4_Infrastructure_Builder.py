
import streamlit as st

from common.banners import data_source_notice
from common.data import HOURS_PER_MONTH
from logic.infrastructure import (
    SUPPORTED_SERVICES,
    REGIONS,
    EC2_INSTANCE_TYPES,
    RDS_INSTANCE_TYPES,
    S3_STORAGE_CLASSES,
    create_scenario,
    validate_scenario,
    save_scenario,
    load_scenarios,
    delete_scenario,
)

st.set_page_config(
    page_title="Infrastructure Builder",
    layout="wide",
)

st.title("Infrastructure Builder")
st.caption("Module 3 | Owner: Bhawan")
data_source_notice("simulated")

st.write(
    "Configure hypothetical cloud infrastructure and "
    "create scenarios for cost estimation."
)

# Scenario details
st.header("1. Scenario Details")

col1, col2 = st.columns(2)

with col1:
    scenario_name = st.text_input(
        "Scenario name",
        placeholder="e.g. E-commerce Application",
    )

with col2:
    region = st.selectbox("AWS Region", REGIONS)

# Service selection
st.header("2. Select Cloud Services")

selected_services = st.multiselect(
    "Select the services required for your infrastructure",
    SUPPORTED_SERVICES,
)

resources = {}

# Resource configuration
st.header("3. Resource Configuration")

if not selected_services:
    st.info("Select at least one cloud service to configure.")

# EC2
if "EC2" in selected_services:
    with st.expander("EC2 Configuration", expanded=True):

        col1, col2 = st.columns(2)

        with col1:
            instance_type = st.selectbox(
                "Instance type", EC2_INSTANCE_TYPES
            )

            instance_count = st.number_input(
                "Number of EC2 instances",
                min_value=1,
                value=3,
                step=1,
            )

            operating_system = st.selectbox(
                "Operating system", ["Linux", "Windows"]
            )

        with col2:
            monthly_hours = st.number_input(
                "EC2 monthly running hours",
                min_value=1,
                max_value=HOURS_PER_MONTH,
                value=HOURS_PER_MONTH,
            )

            storage_gb = st.number_input(
                "EBS storage per instance (GB)",
                min_value=0,
                value=100,
            )

        resources["EC2"] = {
            "instance_type": instance_type,
            "instance_count": instance_count,
            "operating_system": operating_system,
            "monthly_hours": monthly_hours,
            "storage_gb": storage_gb,
        }

# S3
if "S3" in selected_services:
    with st.expander("S3 Configuration", expanded=True):

        col1, col2 = st.columns(2)

        with col1:
            storage_class = st.selectbox(
                "Storage class", S3_STORAGE_CLASSES
            )

        with col2:
            s3_storage = st.number_input(
                "S3 storage (GB)",
                min_value=0,
                value=500,
            )

        resources["S3"] = {
            "storage_class": storage_class,
            "storage_gb": s3_storage,
        }

# DynamoDB
if "DynamoDB" in selected_services:
    with st.expander("DynamoDB Configuration", expanded=True):

        col1, col2, col3 = st.columns(3)

        with col1:
            read_requests = st.number_input(
                "Monthly read requests",
                min_value=0,
                value=1000000,
                step=100000,
            )

        with col2:
            write_requests = st.number_input(
                "Monthly write requests",
                min_value=0,
                value=1000000,
                step=100000,
            )

        with col3:
            dynamodb_storage = st.number_input(
                "DynamoDB storage (GB)",
                min_value=0,
                value=10,
            )

        resources["DynamoDB"] = {
            "read_requests": read_requests,
            "write_requests": write_requests,
            "storage_gb": dynamodb_storage,
        }

# Lambda
if "Lambda" in selected_services:
    with st.expander("Lambda Configuration", expanded=True):

        col1, col2, col3 = st.columns(3)

        with col1:
            invocations = st.number_input(
                "Monthly invocations",
                min_value=0,
                value=2000000,
                step=100000,
            )

        with col2:
            memory_mb = st.number_input(
                "Memory (MB)",
                min_value=128,
                max_value=10240,
                value=128,
                step=1,
            )

        with col3:
            duration_ms = st.number_input(
                "Average execution duration (ms)",
                min_value=1,
                max_value=900000,
                value=200,
            )

        resources["Lambda"] = {
            "invocations": invocations,
            "memory_mb": memory_mb,
            "duration_ms": duration_ms,
        }

# RDS
if "RDS" in selected_services:
    with st.expander("RDS Configuration", expanded=True):

        col1, col2 = st.columns(2)

        with col1:
            rds_instance = st.selectbox(
                "RDS instance type", RDS_INSTANCE_TYPES
            )

            database_engine = st.selectbox(
                "Database engine", ["MySQL", "PostgreSQL"]
            )

            rds_count = st.number_input(
                "Number of RDS instances",
                min_value=1,
                value=1,
            )

        with col2:
            rds_hours = st.number_input(
                "RDS monthly running hours",
                min_value=1,
                max_value=HOURS_PER_MONTH,
                value=HOURS_PER_MONTH,
            )

            rds_storage = st.number_input(
                "RDS storage per instance (GB)",
                min_value=20,
                value=100,
            )

        resources["RDS"] = {
            "instance_type": rds_instance,
            "database_engine": database_engine,
            "instance_count": rds_count,
            "monthly_hours": rds_hours,
            "storage_gb": rds_storage,
        }

# Scenario creation
st.header("4. Create Infrastructure Scenario")

if st.button("Create Scenario", type="primary"):

    errors = validate_scenario(
        scenario_name, region, resources
    )

    if errors:
        for error in errors:
            st.error(error)

    else:
        scenario = create_scenario(
            scenario_name, region, resources
        )

        try:
            save_scenario(scenario)
        except (OSError, ValueError) as error:
            st.error(f"Unable to save scenario: {error}")
        else:
            st.session_state["created_scenario"] = scenario
            st.success("Infrastructure scenario saved successfully!")


# Saved scenarios
st.divider()
st.header("5. Saved Infrastructure Scenarios")

try:
    saved_scenarios = load_scenarios()
except (OSError, ValueError) as error:
    st.error(f"Unable to load scenarios: {error}")
    st.stop()

if not saved_scenarios:
    st.info("No saved scenarios yet.")

else:
    st.metric("Total saved scenarios", len(saved_scenarios))

    summary = [
        {
            "Scenario": scenario["name"],
            "Region": scenario["region"],
            "Services": ", ".join(scenario["resources"].keys()),
            "Service count": len(scenario["resources"]),
        }
        for scenario in saved_scenarios
    ]

    st.dataframe(
        summary,
        hide_index=True,
        use_container_width=True,
    )

    scenario_options = {
        scenario["id"]: scenario
        for scenario in saved_scenarios
    }

    selected_id = st.selectbox(
        "Select a scenario to view",
        options=list(scenario_options.keys()),
        format_func=lambda sid: (
            f"{scenario_options[sid]['name']} "
            f"({scenario_options[sid]['region']}) "
            f"- {sid[:8]}"
        ),
    )

    selected_scenario = scenario_options[selected_id]

    st.subheader(selected_scenario["name"])

    col1, col2 = st.columns(2)

    with col1:
        st.metric("AWS Region", selected_scenario["region"])

    with col2:
        st.metric(
            "Configured services",
            len(selected_scenario["resources"]),
        )

    with st.expander("View infrastructure configuration"):
        st.json(selected_scenario)

    st.caption(
        "Saved scenarios will be available "
        "in Module 4 - Cost Estimator."
    )

    st.subheader("Delete Scenario")

    confirm_delete = st.checkbox(
        "I confirm that I want to delete this scenario.",
        key=f"confirm_delete_{selected_id}",
    )

    if st.button(
        "Delete Selected Scenario",
        disabled=not confirm_delete,
    ):
        try:
            deleted = delete_scenario(selected_id)
        except (OSError, ValueError) as error:
            st.error(f"Unable to delete scenario: {error}")
        else:
            if deleted:
                st.session_state.pop("created_scenario", None)
                st.rerun()
            else:
                st.error("Scenario not found.")

