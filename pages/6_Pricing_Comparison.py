import streamlit as st

from common.banners import data_source_notice

st.set_page_config(page_title="Pricing Comparison", layout="wide")
st.title("Pricing Comparison")
st.caption("Module 5 | Owner: Areeba (TBC)")
data_source_notice("simulated")
st.info("TODO: compare On-Demand, Reserved, Savings Plans, Spot; show savings and limitations of each.")
