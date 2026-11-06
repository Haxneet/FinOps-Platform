"""Labels that separate actual API responses from simulated data."""
import streamlit as st


def data_source_notice(kind: str) -> None:
    """Show a banner. kind is 'actual' (Floci API response) or 'simulated'."""
    if kind == "actual":
        st.success("Data source: actual response from the Floci API.")
    elif kind == "simulated":
        st.warning(
            "Data source: SIMULATED data. These figures are hypothetical and "
            "are not real AWS spend or measurements."
        )
    else:
        raise ValueError("kind must be 'actual' or 'simulated'")
