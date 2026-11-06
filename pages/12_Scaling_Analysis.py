import streamlit as st

from common.banners import data_source_notice

st.set_page_config(page_title="Scaling Analysis", layout="wide")
st.title("Scaling Analysis")
st.caption("Module 12 | Owner: Harneet")
data_source_notice("simulated")
st.info("TODO: fixed vs auto-scaled cost across workload levels, include load balancer cost, show savings.")
