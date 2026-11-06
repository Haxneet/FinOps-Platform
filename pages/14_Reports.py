import streamlit as st

from common.banners import data_source_notice

st.set_page_config(page_title="Reports", layout="wide")
st.title("Reports")
st.caption("Module 8 | Owner: Areeba (TBC)")
data_source_notice("simulated")
st.info("TODO: consolidated management report (spend, service/region/department breakdown, budgets, recommendations, savings) with CSV or PDF download.")
