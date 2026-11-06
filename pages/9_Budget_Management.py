import streamlit as st

from common.banners import data_source_notice

st.set_page_config(page_title="Budget Management", layout="wide")
st.title("Budget Management")
st.caption("Module 9 | Owner: Bhawan")
data_source_notice("simulated")
st.info("TODO: departmental budgets, thresholds (50 / 80 / 100 / above 100 percent), utilization, warnings. Try the Floci Budgets API first.")
