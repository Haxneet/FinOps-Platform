import streamlit as st

from common.banners import data_source_notice

st.set_page_config(page_title="Storage and Backup", layout="wide")
st.title("Storage and Backup")
st.caption("Module 13 | Owner: Harneet")
data_source_notice("simulated")
st.info("TODO: storage by category and access pattern, storage class comparison, lifecycle policies, backup retention comparison, savings.")
