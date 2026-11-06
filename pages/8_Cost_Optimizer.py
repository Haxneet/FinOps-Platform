import streamlit as st

from common.banners import data_source_notice

st.set_page_config(page_title="Cost Optimizer", layout="wide")
st.title("Cost Optimizer")
st.caption("Module 7 | Owner: Areeba (TBC)")
data_source_notice("simulated")
st.info("TODO: rule-based engine, at least 5 recommendations, estimated monthly savings, ranked by impact, original vs optimized comparison.")
