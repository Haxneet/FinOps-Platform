import streamlit as st

from common.banners import data_source_notice

st.set_page_config(page_title="Resource Utilization", layout="wide")
st.title("Resource Utilization")
st.caption("Module 10 | Owner: Unassigned (Areeba has not picked yet)")
data_source_notice("simulated")
st.info("TODO: CPU and memory utilization over time, flag underutilized instances, suggest smaller sizes, estimate savings. Do not judge on CPU alone.")
