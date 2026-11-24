import pandas as pd
import streamlit as st

from common.banners import data_source_notice
from common.pricing import (
    BACKUP_COLD_PER_GB,
    BACKUP_WARM_PER_GB,
    PRICING_SOURCE,
    REGION,
    S3_CLASSES,
)
from logic import storage

st.set_page_config(page_title="Storage and Backup", layout="wide")
st.title("Storage and Backup")
st.caption("Module 13 | Owner: Harneet")
data_source_notice("simulated")

tab1, tab2, tab3, tab4 = st.tabs(
    ["1. Storage analysis", "2. Storage class scenario", "3. Lifecycle policy", "4. Backup retention"]
)

# ======================= Tab 1: current storage =======================
with tab1:
    st.subheader("Current storage and access patterns")
    st.caption("Edit sizes, access patterns and the class each category is stored in today.")
    base = pd.DataFrame(
        [(n, gb, p, "Standard") for n, gb, p in storage.DEFAULT_DATASET],
        columns=["Category", "Size (GB)", "Access pattern", "Current class"],
    )
    data = st.data_editor(
        base,
        num_rows="fixed",
        use_container_width=True,
        key="storage_editor",
        column_config={
            "Access pattern": st.column_config.SelectboxColumn(
                options=list(storage.RETRIEVED_FRACTION)
            ),
            "Current class": st.column_config.SelectboxColumn(options=list(S3_CLASSES)),
        },
    )
    data["Size (GB)"] = pd.to_numeric(data["Size (GB)"], errors="coerce").fillna(0)
    analysis = storage.analyze(data)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total storage", f"{analysis['Size (GB)'].sum():,.0f} GB")
    c2.metric("Current monthly cost", f"${analysis['Current monthly cost'].sum():,.2f}")
    c3.metric("Annual cost", f"${analysis['Current monthly cost'].sum() * 12:,.2f}")

    left, right = st.columns(2)
    with left:
        st.markdown("**Storage by category (GB)**")
        st.bar_chart(analysis.set_index("Category")["Size (GB)"])
    with right:
        st.markdown("**Monthly cost by category (USD)**")
        st.bar_chart(analysis.set_index("Category")["Current monthly cost"])

    st.markdown("**Storage class prices used**")
    price_table = pd.DataFrame(
        [
            {
                "Class": name,
                "Storage (USD/GB-month)": p["storage"],
                "Retrieval (USD/GB)": p["retrieval"],
                "Retrieval time": p["retrieval_time"],
            }
            for name, p in S3_CLASSES.items()
        ]
    )
    st.dataframe(price_table, use_container_width=True, hide_index=True)

# ======================= Tab 2: class scenario =======================
with tab2:
    st.subheader("Scenario A: move data to the cheapest suitable storage class")
    st.caption(
        "For each category the cheapest class is chosen from the classes that suit its access "
        "pattern. Frequently used data stays in Standard."
    )
    st.dataframe(analysis, use_container_width=True, hide_index=True)

    savings = analysis["Monthly savings"].sum()
    current_total = analysis["Current monthly cost"].sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Monthly savings", f"${savings:,.2f}")
    c2.metric("Annual savings", f"${savings * 12:,.2f}")
    c3.metric("Reduction", f"{(savings / current_total * 100) if current_total else 0:.1f}%")

    st.markdown("**Current vs recommended monthly cost**")
    st.bar_chart(
        analysis.set_index("Category")[["Current monthly cost", "Recommended monthly cost"]]
    )

    slow = analysis[analysis["Retrieval time"] != "Immediate"]
    if not slow.empty:
        st.warning(
            "Some recommended classes are not instant to read: "
            + ", ".join(f"{r['Category']} ({r['Retrieval time'].lower()})" for _, r in slow.iterrows())
            + ". Confirm this meets business requirements before moving the data."
        )

    st.download_button(
        "Download storage analysis (CSV)",
        analysis.to_csv(index=False).encode("utf-8"),
        file_name="storage_analysis.csv",
        mime="text/csv",
    )

# ======================= Tab 3: lifecycle =======================
with tab3:
    st.subheader("Scenario B: S3 lifecycle policy on a growing bucket")
    st.caption("Compares keeping everything in Standard with moving older data to cheaper classes.")

    c1, c2 = st.columns(2)
    with c1:
        ingest = st.number_input("New data per month (GB)", 1.0, 100000.0, 100.0, 10.0)
        months = st.slider("Months to simulate", 3, 36, 12)
        ia_days = st.number_input("Move to Standard-IA after (days)", 0, 365, 30, 30)
    with c2:
        archive_days = st.number_input("Move to archive class after (days)", 30, 730, 90, 30)
        archive_class = st.selectbox(
            "Archive class",
            ["Glacier Instant Retrieval", "Glacier Flexible Retrieval", "Deep Archive"],
            index=1,
        )
        use_expiry = st.checkbox("Delete data after a set age", value=False)
        expire_days = st.number_input("Delete after (days)", 30, 3650, 365, 30) if use_expiry else None
    read_pct = st.slider("Share of archived data read back each month (%)", 0.0, 20.0, 2.0, 0.5)

    if archive_days < ia_days:
        st.error("The archive transition must come after the Standard-IA transition.")
    else:
        life = storage.lifecycle_simulation(
            float(ingest), int(months), int(ia_days), int(archive_days),
            archive_class, int(expire_days) if expire_days else None, float(read_pct),
        )
        last = life.iloc[-1]
        c1, c2, c3 = st.columns(3)
        c1.metric(f"Month {months}: no policy", f"${last['No policy cost']:,.2f}")
        c2.metric(f"Month {months}: with policy", f"${last['With policy cost']:,.2f}")
        c3.metric("Monthly savings at end", f"${last['Monthly savings']:,.2f}")
        st.info(
            f"Total over {months} months: ${life['No policy cost'].sum():,.2f} without a policy "
            f"vs ${life['With policy cost'].sum():,.2f} with it, a saving of "
            f"${life['Monthly savings'].sum():,.2f}."
        )

        st.markdown("**Monthly storage cost**")
        st.line_chart(life.set_index("Month")[["No policy cost", "With policy cost"]])
        st.markdown("**Data stored (GB)**")
        st.line_chart(life.set_index("Month")[["No policy (GB)", "With policy (GB)"]])
        st.dataframe(life, use_container_width=True, hide_index=True)
        st.download_button(
            "Download lifecycle simulation (CSV)",
            life.to_csv(index=False).encode("utf-8"),
            file_name="lifecycle_simulation.csv",
            mime="text/csv",
        )

# ======================= Tab 4: backup retention =======================
with tab4:
    st.subheader("Backup storage and retention")
    st.caption("How the retention period changes backup storage and cost.")

    c1, c2 = st.columns(2)
    with c1:
        backup_gb = st.number_input("Protected data (GB)", 1.0, 100000.0, 400.0, 50.0)
        change_pct = st.slider("Daily data change (%)", 0.1, 20.0, 3.0, 0.1)
    with c2:
        current_ret = st.selectbox("Current retention (days)", [7, 14, 30, 60, 90, 180, 365], index=4)
        use_cold = st.checkbox("Move older backups to cold storage", value=False)
        cold_days = st.number_input("Move to cold storage after (days)", 1, 365, 30, 1) if use_cold else None

    options = [7, 14, 30, 60, 90, 180, 365]
    ret = storage.backup_retention(
        float(backup_gb), float(change_pct), options, int(current_ret),
        int(cold_days) if cold_days else None,
    )
    st.dataframe(ret, use_container_width=True, hide_index=True)

    current_row = ret[ret["Retention (days)"] == current_ret].iloc[0]
    st.metric("Current backup cost (monthly)", f"${current_row['Monthly cost']:,.2f}")

    st.markdown("**Monthly backup cost by retention period**")
    st.bar_chart(ret.set_index("Retention (days)")["Monthly cost"])
    st.warning(
        "Retention periods are often set by compliance or recovery requirements. "
        "Shorter retention lowers cost but reduces how far back you can restore."
    )
    st.download_button(
        "Download backup retention analysis (CSV)",
        ret.to_csv(index=False).encode("utf-8"),
        file_name="backup_retention.csv",
        mime="text/csv",
    )

# ======================= Assumptions =======================
with st.expander("Assumptions and exclusions"):
    st.markdown(
        f"""
- **Pricing source:** {PRICING_SOURCE}
- **Region:** {REGION}
- **Pricing model:** S3 On-Demand storage and retrieval prices; AWS Backup warm storage ${BACKUP_WARM_PER_GB}/GB-month and cold storage ${BACKUP_COLD_PER_GB}/GB-month.
- **Billing period:** one month.
- **Usage:** the dataset is the assignment example and is simulated, not read from S3. The share of data read back each month is assumed: Frequent 100%, Periodic 20%, Infrequent 5%, Rare 1%.
- **Allowed classes:** Frequent data stays in Standard; Periodic can use Standard-IA; Infrequent can also use Glacier Instant Retrieval; Rare data can use all classes.
- **Lifecycle:** each month's batch of data is treated as 30 days older than the next batch.
- **Backups:** incremental-forever model, one full copy plus the changed data for each retained day.
- **Excluded:** lifecycle transition request fees, minimum storage duration charges, early deletion fees, request charges, data transfer, cross-region copies, taxes and discounts.
- Savings are estimates and must be checked against retrieval time and compliance needs before any change.
"""
    )
