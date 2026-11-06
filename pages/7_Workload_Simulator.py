import streamlit as st

from common.banners import data_source_notice

st.set_page_config(page_title="Workload Simulator", layout="wide")
st.title("Workload Simulator")
st.caption("Module 6 | Owner: Harneet")
data_source_notice("simulated")
st.info("TODO: adjust monthly request levels, compute required infrastructure and cost, compare low/medium/high.")
