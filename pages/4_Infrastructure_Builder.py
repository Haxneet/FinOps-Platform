import streamlit as st

from common.banners import data_source_notice

st.set_page_config(page_title="Infrastructure Builder", layout="wide")
st.title("Infrastructure Builder")
st.caption("Module 3 | Owner: Bhawan")
data_source_notice("simulated")
st.info("TODO: form to configure EC2, S3, DynamoDB, Lambda, RDS; save multiple scenarios.")
