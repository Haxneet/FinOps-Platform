import pandas as pd
import streamlit as st

from common.banners import data_source_notice
from common.pricing import ALB_HOURLY, EC2_HOURLY, PRICING_SOURCE, REGION
from logic import scaling

st.set_page_config(page_title="Scaling Analysis", layout="wide")
st.title("Scaling Analysis")
st.caption("Module 12 | Owner: Harneet")
data_source_notice("simulated")

st.write(
    "Is it cheaper to run a fixed number of EC2 instances all month, or to let "
    "Auto Scaling add and remove instances as demand changes?"
)

# ---------------- Sidebar inputs ----------------
with st.sidebar:
    st.header("Infrastructure")
    instance_type = st.selectbox("EC2 instance type", list(EC2_HOURLY), index=1)
    fixed_count = st.number_input("Fixed fleet size (instances)", 1, 50, 8, 1)
    min_inst = st.number_input("Auto Scaling minimum", 1, 50, 2, 1)
    max_inst = st.number_input("Auto Scaling maximum", 1, 100, 8, 1)
    overhead = st.slider("Scaling overhead (%)", 0, 50, 10,
                         help="Extra instance-hours from warm-up, cooldown and scale-out lag.")
    lcu = st.number_input("Average load balancer LCUs", 0.0, 100.0, 5.0, 0.5)

if min_inst > max_inst:
    st.error("The Auto Scaling minimum cannot be higher than the maximum.")
    st.stop()

# ---------------- Workload profile ----------------
st.subheader("1. Workload profile")
st.caption("How many instances each level needs, and how much of the month is spent at each level.")
profile = pd.DataFrame(
    {
        "Workload level": scaling.LEVELS,
        "Instances required": [scaling.DEFAULT_REQUIRED[l] for l in scaling.LEVELS],
        "Share of month (%)": [scaling.DEFAULT_SHARE_PCT[l] for l in scaling.LEVELS],
    }
)
profile = st.data_editor(profile, num_rows="fixed", use_container_width=True, key="profile_editor")
required = {r["Workload level"]: int(r["Instances required"]) for _, r in profile.iterrows()}
share = {r["Workload level"]: float(r["Share of month (%)"]) for _, r in profile.iterrows()}

total_share = sum(share.values())
if abs(total_share - 100) > 0.01:
    if total_share <= 0:
        st.error("Shares must add up to more than zero.")
        st.stop()
    st.warning(f"Shares add up to {total_share:.1f}%, not 100%. They have been scaled to 100%.")
    share = {k: v * 100 / total_share for k, v in share.items()}

# ---------------- Main comparison ----------------
res = scaling.compare(
    instance_type, int(fixed_count), int(min_inst), int(max_inst),
    required, share, float(overhead), float(lcu),
)

st.subheader("2. Fixed infrastructure vs Auto Scaling")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Fixed (monthly)", f"${res['fixed_monthly']:,.2f}")
c2.metric("Auto Scaling (monthly)", f"${res['auto_monthly']:,.2f}")
c3.metric("Monthly savings", f"${res['savings_monthly']:,.2f}", f"{res['savings_pct']:.1f}%")
c4.metric("Annual savings", f"${res['savings_annual']:,.2f}")

if res["fixed_under_capacity_pct"] > 0:
    st.warning(
        f"The fixed fleet of {int(fixed_count)} is smaller than required for "
        f"{res['fixed_under_capacity_pct']:.1f}% of the month. It looks cheaper only "
        "because it cannot serve peak demand, which risks slow responses or outages."
    )
if (res["table"]["Auto scaling status"] == "Capped at max").any():
    st.warning("The Auto Scaling maximum is lower than the instances required at some levels.")

st.dataframe(res["table"], use_container_width=True, hide_index=True)

left, right = st.columns(2)
with left:
    st.markdown("**Instances running by workload level**")
    st.bar_chart(
        res["table"].set_index("Workload level")[
            ["Instances required", "Fixed running", "Auto scaling running"]
        ]
    )
with right:
    st.markdown("**Monthly EC2 cost by workload level**")
    st.bar_chart(
        res["table"].set_index("Workload level")[["Fixed EC2 cost", "Auto scaling EC2 cost"]]
    )

st.markdown(
    f"Load balancer cost is the same for both approaches: **${res['alb_monthly']:,.2f}** per month "
    f"(${ALB_HOURLY}/hour plus {lcu} average LCUs)."
)

# ---------------- Fixed sizing strategies ----------------
st.subheader("3. Other ways to size a fixed fleet")
strategies = scaling.strategy_table(
    instance_type, int(min_inst), int(max_inst), required, share, float(overhead), float(lcu)
)
st.dataframe(strategies, use_container_width=True, hide_index=True)
st.caption(
    "A fixed fleet sized below peak is cheaper but is under capacity for part of the month. "
    "Only the peak-sized fleet is a fair comparison for availability."
)

# ---------------- Promotion sensitivity ----------------
st.subheader("4. What if promotions make Very high demand more common?")
shares_to_test = [0, 2.5, 5, 10, 15, 20, 30]
sweep = scaling.peak_share_sweep(
    instance_type, int(fixed_count), int(min_inst), int(max_inst),
    required, share, float(overhead), float(lcu), shares_to_test,
)
st.line_chart(sweep.set_index("Very high share (%)"))
st.dataframe(sweep, use_container_width=True, hide_index=True)

# ---------------- Export and assumptions ----------------
st.download_button(
    "Download scaling analysis (CSV)",
    res["table"].to_csv(index=False).encode("utf-8"),
    file_name="scaling_analysis.csv",
    mime="text/csv",
)

with st.expander("Assumptions and exclusions"):
    st.markdown(
        f"""
- **Pricing source:** {PRICING_SOURCE}
- **Region:** {REGION}
- **Pricing model:** On-Demand for both approaches ({instance_type} at ${EC2_HOURLY[instance_type]}/hour).
- **Billing period:** one month of 730 hours.
- **Fixed infrastructure:** {int(fixed_count)} instances running all month.
- **Auto Scaling:** instances follow demand between {int(min_inst)} and {int(max_inst)}; a {overhead}% overhead is added for warm-up and cooldown.
- **Workload profile:** the share of the month at each level is an assumption you can change above. Instances required per level come from the assignment example.
- **Load balancer:** same cost in both cases, so it does not change the savings.
- **Excluded:** taxes, data transfer, storage, database, Spot or Reserved pricing, launch template costs, and any application performance impact.
- Savings are hypothetical until performance and availability are tested.
"""
    )
