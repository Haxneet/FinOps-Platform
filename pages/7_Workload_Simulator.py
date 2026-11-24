import pandas as pd
import streamlit as st

from common.banners import data_source_notice
from common.pricing import EC2_HOURLY, PRICING_SOURCE, REGION, RDS_HOURLY
from logic import workload

st.set_page_config(page_title="Workload Simulator", layout="wide")
st.title("Workload Simulator")
st.caption("Module 6 | Owner: Harneet")
data_source_notice("simulated")

st.write(
    "Change the monthly request volume and see how many EC2 instances the "
    "application needs and what that does to monthly cloud cost."
)

# ---------------- Sidebar: infrastructure assumptions ----------------
with st.sidebar:
    st.header("Infrastructure assumptions")
    instance_type = st.selectbox("EC2 instance type", list(EC2_HOURLY), index=1)
    rps = st.number_input("Requests per second one instance can serve", 1.0, 500.0, 8.0, 1.0)
    peak = st.number_input("Peak traffic vs monthly average (x)", 1.0, 20.0, 5.0, 0.5)
    min_inst = st.number_input("Minimum instances (availability)", 1, 10, 2, 1)
    kb = st.number_input("Average response size (KB)", 1.0, 5000.0, 150.0, 10.0)
    include_rds = st.checkbox("Include database (RDS)", value=True)
    rds_type = st.selectbox("RDS instance type", list(RDS_HOURLY), index=0)

cfg = workload.WorkloadConfig(
    instance_type=instance_type,
    rps_per_instance=float(rps),
    peak_factor=float(peak),
    min_instances=int(min_inst),
    avg_response_kb=float(kb),
    include_rds=include_rds,
    rds_type=rds_type,
)

# ---------------- Workload editor ----------------
st.subheader("1. Monthly workload")
st.caption("Edit the request volumes to test your own scenarios.")
base = pd.DataFrame(workload.DEFAULT_MONTHLY_REQUESTS, columns=["Period", "Monthly requests"])
edited = st.data_editor(base, num_rows="fixed", use_container_width=True, key="wl_editor")
edited["Monthly requests"] = pd.to_numeric(edited["Monthly requests"], errors="coerce").fillna(0)

rows = list(zip(edited["Period"], edited["Monthly requests"]))
result = workload.simulate(rows, cfg)

# ---------------- Results ----------------
st.subheader("2. Infrastructure and cost for each month")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Lowest monthly cost", f"${result['Total monthly cost'].min():,.2f}")
c2.metric("Highest monthly cost", f"${result['Total monthly cost'].max():,.2f}")
c3.metric("Total for the period", f"${result['Total monthly cost'].sum():,.2f}")
c4.metric("Peak instances", int(result["EC2 instances"].max()))

st.dataframe(result, use_container_width=True, hide_index=True)

left, right = st.columns(2)
with left:
    st.markdown("**Workload growth (monthly requests)**")
    st.bar_chart(result.set_index("Period")["Monthly requests"])
with right:
    st.markdown("**Expenditure (USD per month)**")
    st.line_chart(result.set_index("Period")["Total monthly cost"])

st.markdown("**Cost breakdown by component**")
st.bar_chart(
    result.set_index("Period")[
        ["EC2 cost", "Load balancer cost", "Database cost", "Data transfer cost"]
    ]
)

first, last = result.iloc[0], result.iloc[-1]
if first["Monthly requests"] > 0:
    growth = last["Monthly requests"] / first["Monthly requests"]
    cost_growth = last["Total monthly cost"] / first["Total monthly cost"]
    st.info(
        f"From {first['Period']} to {last['Period']} the workload grows {growth:,.1f}x "
        f"while monthly cost grows {cost_growth:,.1f}x. Cost per million requests falls "
        f"from ${first['Cost per 1M requests']:,.2f} to ${last['Cost per 1M requests']:,.2f}, "
        "because fixed costs such as the database and minimum fleet are spread over more traffic."
    )

# ---------------- Low / medium / high comparison ----------------
st.subheader("3. Compare low, medium and high workloads")
scen_base = pd.DataFrame(workload.DEFAULT_SCENARIOS, columns=["Scenario", "Monthly requests"])
scen_edit = st.data_editor(scen_base, num_rows="fixed", use_container_width=True, key="scen_editor")
scen_edit["Monthly requests"] = pd.to_numeric(scen_edit["Monthly requests"], errors="coerce").fillna(0)
scen_result = workload.simulate(list(zip(scen_edit["Scenario"], scen_edit["Monthly requests"])), cfg)
st.dataframe(scen_result, use_container_width=True, hide_index=True)
st.bar_chart(scen_result.set_index("Period")["Total monthly cost"])

# ---------------- Export and assumptions ----------------
st.download_button(
    "Download workload results (CSV)",
    result.to_csv(index=False).encode("utf-8"),
    file_name="workload_simulation.csv",
    mime="text/csv",
)

with st.expander("Assumptions and exclusions"):
    st.markdown(
        f"""
- **Pricing source:** {PRICING_SOURCE}
- **Region:** {REGION}
- **Pricing model:** On-Demand, running 730 hours per month.
- **Resource configuration:** {instance_type} application servers behind an Application Load Balancer; {rds_type if include_rds else 'no database'}.
- **Billing period:** one calendar month per row.
- **Sizing rule:** instances = peak requests per second divided by capacity per instance, rounded up, never below the minimum. The fleet is sized for the monthly peak and runs all month, so this is a conservative estimate.
- **Peak requests per second** = monthly requests / 2,628,000 seconds x peak factor.
- **Load balancer:** hourly charge plus LCUs estimated from data processed and request rate (simplified).
- **Data transfer:** response size x requests x $0.09 per GB, free tier ignored.
- **Excluded:** taxes, discounts, storage, backups, CloudWatch, NAT gateways, cross-AZ traffic, and request-based charges for other services.
- All figures are simulated estimates, not actual AWS spend.
"""
    )
