import streamlit as st

from common.banners import data_source_notice

st.set_page_config(page_title="Cost Explorer", layout="wide")
st.title("Cost Explorer")
st.caption("Module 2 | Owner: Unassigned (Areeba has not picked yet)")
data_source_notice("simulated")
st.info("TODO: test Floci Cost Explorer ops; fall back to synthetic billing data. Show total, monthly, by service, by region, daily trend, top services, period comparison, export.")
