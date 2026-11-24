import streamlit as st

from common.banners import data_source_notice

st.set_page_config(page_title="Cost Allocation", layout="wide")
st.title("Cost Allocation")
st.caption("Module 11 | Owner: Unassigned (Areeba has not picked yet)")
data_source_notice("simulated")
st.info("TODO: tags (Department, Project, Environment, Owner, CostCenter), spend by department/project/environment, untagged and incomplete resources.")
