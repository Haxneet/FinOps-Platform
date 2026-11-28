
# Module 3 - Cloud Infrastructure Configuration Builder

**Developer:** Bhawandeep Kaur Gill

## 1. Overview

The Infrastructure Configuration Builder allows users to
create hypothetical AWS infrastructure scenarios by selecting
cloud services, regions, resource quantities and expected usage.

The saved configurations will be used by Module 4
to estimate infrastructure costs.

## 2. Supported AWS Services

| Service | Configuration |
|---|---|
| EC2 | Instance type, quantity, OS, usage hours and storage |
| S3 | Storage class and storage capacity |
| DynamoDB | Read requests, write requests and storage |
| Lambda | Invocations, memory and execution duration |
| RDS | Instance type, database engine, quantity, hours and storage |

## 3. Supported Regions

- us-east-1
- us-west-2
- ca-central-1

## 4. Main Features

- Create multiple infrastructure scenarios.
- Configure individual AWS services.
- Validate user inputs.
- Save and retrieve infrastructure configurations.
- Display saved scenarios in a summary table.
- View detailed resource configurations.
- Delete scenarios with user confirmation.
- Provide infrastructure configurations for Module 4.

## 5. Implementation

The module uses Streamlit for the user interface and
Python for backend logic.

Main files:

- pages/4_Infrastructure_Builder.py
- logic/infrastructure.py
- tests/test_module_3.py

Backend functions:

- validate_scenario(): Validates infrastructure inputs.
- create_scenario(): Creates a scenario with a unique ID.
- save_scenario(): Saves a scenario to JSON storage.
- load_scenarios(): Retrieves saved scenarios.
- delete_scenario(): Removes a scenario using its ID.

## 6. Data Storage

Scenarios are stored locally in:

data/scenarios/infrastructure_scenarios.json

Each scenario contains a unique ID, name, region,
creation timestamp and resource configurations.

The generated storage directory is excluded from Git.

## 7. Assumptions and Limitations

- All infrastructure configurations are hypothetical.
- No actual AWS resources are provisioned.
- Monthly instance usage is limited to 730 hours.
- Supported services and regions are predefined.
- JSON storage is intended for local, single-user use.
- Existing scenarios cannot currently be edited.
- Cost calculations are handled separately by Module 4.

## 8. Testing

Automated tests cover scenario creation, input validation,
persistent storage, retrieval and deletion.

Run Module 3 tests:

    python -m pytest tests/test_module_3.py -v

Run all project tests:

    python -m pytest -v

Results:

- Module 3: 16 automated tests passed.
- Full project test suite: 33 tests passed.
- Saved scenario management: 7/7 manual checks passed.
- Final infrastructure testing: 7/7 manual checks passed.

## 9. Technologies Used

- Python
- Streamlit
- JSON
- UUID
- Pytest
- Git and GitHub

## 10. Integration with Module 4

Module 4 will retrieve saved infrastructure scenarios
using load_scenarios() and calculate estimated costs
based on resource configurations, usage and pricing.
