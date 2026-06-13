"""Streamlit UI for AI tool intake, decisions, and governance dashboard."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from audit_logger import read_audit_log, write_audit_record
from policy_engine import evaluate_policies
from risk_scorer import calculate_risk

st.set_page_config(page_title="AI Tool Governance Ops", page_icon="🛡️", layout="wide")

VENDOR_TYPES = ["internal", "external", "open-source"]
DATA_TYPES = ["public", "internal", "confidential", "customer data", "PII"]
REQUESTED_USES = ["pilot", "production"]


def render_intake_form() -> None:
    st.header("AI Tool Intake Form")
    st.caption("Submit AI tools through a structured workflow instead of ad hoc email, Slack, or spreadsheets.")

    with st.form("ai_tool_intake"):
        col1, col2 = st.columns(2)
        with col1:
            tool_name = st.text_input("Tool name")
            business_use_case = st.text_area("Business use case")
            requesting_team = st.text_input("Requesting team")
            owner = st.text_input("Owner")
            vendor_type = st.selectbox("Vendor type", VENDOR_TYPES)
        with col2:
            data_type = st.selectbox("Data type", DATA_TYPES)
            uses_customer_data = st.radio("Uses customer data", ["no", "yes"], horizontal=True)
            uses_pii = st.radio("Uses PII", ["no", "yes"], horizontal=True)
            estimated_monthly_usage = st.number_input("Estimated monthly usage", min_value=0, step=100)
            estimated_monthly_cost = st.number_input("Estimated monthly cost", min_value=0.0, step=50.0, format="%.2f")
            requested_use = st.selectbox("Requested use", REQUESTED_USES)
        submitted = st.form_submit_button("Evaluate request")

    if submitted:
        request = {
            "tool_name": tool_name,
            "business_use_case": business_use_case,
            "requesting_team": requesting_team,
            "owner": owner,
            "vendor_type": vendor_type,
            "data_type": data_type,
            "uses_customer_data": uses_customer_data,
            "uses_pii": uses_pii,
            "estimated_monthly_usage": estimated_monthly_usage,
            "estimated_monthly_cost": estimated_monthly_cost,
            "requested_use": requested_use,
        }
        risk_result = calculate_risk(request)
        policy_result = evaluate_policies(request, risk_result)
        audit_record = write_audit_record(request, risk_result, policy_result)
        render_decision(risk_result, policy_result, audit_record["request_id"])


def render_decision(risk_result: dict, policy_result: dict, request_id: str) -> None:
    st.subheader("Decision Output")
    col1, col2, col3 = st.columns(3)
    col1.metric("Risk level", risk_result["risk_level"].title())
    col2.metric("Risk score", risk_result["risk_score"])
    col3.metric("Decision", policy_result["decision"])
    st.write(risk_result["explanation"])
    st.write(f"Request ID: `{request_id}`")

    st.markdown("**Required reviews**")
    st.write(policy_result["required_reviews"] or ["No additional reviews required"])
    st.markdown("**Required controls**")
    for control in policy_result["required_controls"]:
        st.write(f"- {control}")


def render_dashboard() -> None:
    st.header("Governance Dashboard")
    records = read_audit_log()
    if not records:
        st.info("No audit log entries yet. Submit a request to populate the dashboard.")
        return

    df = pd.DataFrame(records)
    total = len(df)
    approved = df["decision"].str.contains("Approved", na=False).sum()
    requiring_review = total - approved
    high_risk = (df["risk_level"] == "high").sum()
    spend = pd.to_numeric(df.get("estimated_monthly_cost", 0), errors="coerce").fillna(0).sum()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total reviewed", total)
    col2.metric("Approved tools", int(approved))
    col3.metric("Requiring review", int(requiring_review))
    col4.metric("High risk", int(high_risk))
    col5.metric("Monthly AI spend", f"${spend:,.0f}")

    st.subheader("Requests by risk level")
    st.bar_chart(df["risk_level"].value_counts())

    st.subheader("Recent audit log entries")
    st.dataframe(df.sort_values("timestamp", ascending=False).head(10), use_container_width=True)


def main() -> None:
    st.title("🛡️ AI Tool Governance Ops")
    tab1, tab2 = st.tabs(["Intake & Decision", "Dashboard"])
    with tab1:
        render_intake_form()
    with tab2:
        render_dashboard()


if __name__ == "__main__":
    main()
