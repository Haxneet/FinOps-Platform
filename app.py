import streamlit as st

from common.banners import data_source_notice

st.set_page_config(page_title="Cloud FinOps Platform", layout="wide")
st.title("Intelligent Cloud FinOps Platform")
st.caption("Home | Owner: Areeba (TBC)")
data_source_notice("simulated")
st.info("TODO: overall cloud cost summary (total spend, budget status, top services, savings found).")
