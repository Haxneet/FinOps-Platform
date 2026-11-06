import streamlit as st

from common.banners import data_source_notice

st.set_page_config(page_title="Cost Estimator", layout="wide")
st.title("Cost Estimator")
st.caption("Module 4 | Owner: Bhawan")
data_source_notice("simulated")
st.info("TODO: take scenario from Infrastructure Builder, compute hourly/daily/monthly/annual cost per service and resource, document assumptions.")
