import streamlit as st

from common.banners import data_source_notice

st.set_page_config(page_title="Pricing Explorer", layout="wide")
st.title("Pricing Explorer")
st.caption("Module 1 | Owner: Areeba (TBC)")
data_source_notice("actual")
st.info("TODO: pick a service and region, retrieve prices via the Floci Pricing API, store results for other modules.")
