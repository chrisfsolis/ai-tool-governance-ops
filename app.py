"""Streamlit UI for AI tool intake, decisions, audit review, and governance dashboard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from audit_logger import read_audit_log, write_audit_record
from policy_engine import evaluate_policies, load_policies
from risk_scorer import calculate_risk

st.set_page_config(page_title="AI Tool Governance Ops", page_icon="🛡️", layout="wide")

SAMPLE_DATA_PATH = Path("data/sample_ai_tool_requests.csv")
VENDOR_TYPES = ["internal", "external", "open-source"]
DATA_TYPES = ["public", "internal", "confidential", "customer data", "PII"]
REQUESTED_USES = ["pilot", "production"]


def score_request(request: dict[str, Any]) -> dict[str, Any]:
    risk_result = calculate_risk(request)
    policy_result = evaluate_policies(request, risk_result)
    return {**request, **risk_result, **policy_result}


def render_overview() -> None:
    st.title("AI Tool Governance Ops")
    st.info(
        "This demo replaces ad hoc AI tool approvals with a repeatable governance workflow for intake, "
        "risk evaluation, policy review, audit logging, and dashboard monitoring."
    )
    st.write(
        "It shows how low-risk experimentation can move quickly while higher-risk AI use cases are routed "
        "through privacy, security, vendor, finance, or leadership review."
    )
    st.subheader("What the workflow demonstrates")
    st.markdown(
        """
        - Structured intake for AI tool requests
        - Transparent risk scoring and stakeholder-friendly explanations
        - Policy-based review routing and required controls
        - Append-only audit evidence for governance reporting
        - Dashboard monitoring for risk, spend, vendors, and data types
        """
    )


def render_submit() -> None:
    st.header("Submit AI Tool Request")
    st.caption("Submit AI tools through a structured workflow instead of ad hoc email, Slack, or spreadsheets.")

    with st.form("ai_tool_intake"):
        col1, col2 = st.columns(2)
        with col1:
            tool_name = st.text_input("Tool name", value="New AI Assistant")
            business_use_case = st.text_area("Business use case", value="Summarize internal project updates")
            requesting_team = st.text_input("Requesting team", value="Operations")
            business_owner = st.text_input("Business owner", value="Alex Owner")
            vendor_name = st.text_input("Vendor name", value="Internal AI Platform")
            vendor_type = st.selectbox("Vendor type", VENDOR_TYPES)
        with col2:
            data_type = st.selectbox("Data type", DATA_TYPES)
            uses_pii = st.radio("Uses PII", ["no", "yes"], horizontal=True)
            uses_customer_data = st.radio("Uses customer data", ["no", "yes"], horizontal=True)
            requested_use = st.selectbox("Requested use", REQUESTED_USES)
            estimated_monthly_usage = st.number_input("Estimated monthly usage", min_value=0, step=100, value=500)
            estimated_monthly_cost = st.number_input("Estimated monthly cost", min_value=0.0, step=50.0, value=100.0, format="%.2f")
            notes = st.text_area("Notes / justification", value="Pilot request with documented owner and limited scope.")
        submitted = st.form_submit_button("Evaluate and log request")

    if submitted:
        request = {
            "tool_name": tool_name,
            "business_use_case": business_use_case,
            "requesting_team": requesting_team,
            "business_owner": business_owner,
            "owner": business_owner,
            "vendor_name": vendor_name,
            "vendor_type": vendor_type,
            "data_type": data_type,
            "uses_pii": uses_pii,
            "uses_customer_data": uses_customer_data,
            "requested_use": requested_use,
            "estimated_monthly_usage": estimated_monthly_usage,
            "estimated_monthly_cost": estimated_monthly_cost,
            "notes": notes,
        }
        risk_result = calculate_risk(request)
        policy_result = evaluate_policies(request, risk_result)
        audit_record = write_audit_record(request, risk_result, policy_result)
        render_result_card(risk_result, policy_result, audit_record)


def render_result_card(risk_result: dict[str, Any], policy_result: dict[str, Any], audit_record: dict[str, Any]) -> None:
    st.success("Request evaluated and written to the audit log.")
    with st.container(border=True):
        st.subheader("Governance Decision Card")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Request ID", audit_record["request_id"][:8])
        col2.metric("Risk score", risk_result["risk_score"])
        col3.metric("Risk level", risk_result["risk_level"].title())
        col4.metric("Decision", policy_result["decision"])
        st.write(f"**Risk explanation:** {risk_result['explanation']}")
        triggered = [rule.get("name") or rule.get("label") for rule in policy_result.get("triggered_rules", [])]
        st.write("**Triggered policy rules:**", triggered or ["No additional policy rules triggered"])
        st.write("**Required reviews:**", policy_result["required_reviews"] or ["No additional reviews required"])
        st.write("**Required controls:**")
        for control in policy_result["required_controls"]:
            st.markdown(f"- {control}")
        st.write("**Audit log status:** Written successfully")


def load_dashboard_data() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if SAMPLE_DATA_PATH.exists():
        rows.extend(pd.read_csv(SAMPLE_DATA_PATH).to_dict("records"))
    rows.extend(read_audit_log())
    enriched = []
    for row in rows:
        if "decision" in row and "risk_score" in row:
            enriched.append(row)
        else:
            enriched.append(score_request(row))
    return pd.DataFrame(enriched)


def render_dashboard() -> None:
    st.header("Governance Dashboard")
    df = load_dashboard_data()
    if df.empty:
        st.info("No sample or audit records are available yet.")
        return
    df["estimated_monthly_cost"] = pd.to_numeric(df["estimated_monthly_cost"], errors="coerce").fillna(0)
    df["risk_score"] = pd.to_numeric(df["risk_score"], errors="coerce").fillna(0)

    cols = st.columns(7)
    metrics = [
        ("Total reviewed", len(df)),
        ("Approved for pilot", (df["decision"] == "Approved for pilot").sum()),
        ("Approved with controls", (df["decision"] == "Approved with controls").sum()),
        ("Requires additional review", (df["decision"] == "Requires additional review").sum()),
        ("High-risk requests", (df["risk_level"] == "high").sum()),
        ("Monthly AI spend", f"${df['estimated_monthly_cost'].sum():,.0f}"),
        ("Average risk score", f"{df['risk_score'].mean():.1f}"),
    ]
    for col, (label, value) in zip(cols, metrics):
        col.metric(label, value)

    c1, c2, c3 = st.columns(3)
    c1.subheader("Requests by risk level")
    c1.bar_chart(df["risk_level"].value_counts())
    c2.subheader("Requests by vendor type")
    c2.bar_chart(df["vendor_type"].value_counts())
    c3.subheader("Requests by data type")
    c3.bar_chart(df["data_type"].value_counts())
    c4, c5 = st.columns(2)
    c4.subheader("Top 5 highest-risk tools")
    c4.dataframe(df.sort_values("risk_score", ascending=False)[["tool_name", "risk_score", "risk_level", "decision"]].head(5), use_container_width=True)
    c5.subheader("Top 5 highest-cost tools")
    c5.dataframe(df.sort_values("estimated_monthly_cost", ascending=False)[["tool_name", "estimated_monthly_cost", "decision"]].head(5), use_container_width=True)


def render_audit_log() -> None:
    st.header("Audit Log")
    records = read_audit_log()
    if not records:
        st.info("The audit log exists but is empty. Submit a request to create the first audit record.")
        return
    df = pd.DataFrame(records)
    cols = ["timestamp", "request_id", "tool_name", "owner", "risk_level", "decision", "required_reviews", "estimated_monthly_cost"]
    st.dataframe(df[[c for c in cols if c in df.columns]].sort_values("timestamp", ascending=False), use_container_width=True)


def render_policy_rules() -> None:
    st.header("Policy Rules")
    policies = load_policies()
    for rule in policies.get("reviews", []):
        with st.container(border=True):
            st.subheader(rule.get("name", rule.get("label")))
            st.write(rule.get("description"))
            st.write(f"**Condition:** `{rule.get('when')}`")
            st.write(f"**Severity:** {rule.get('severity', 'not specified').title()}")
            st.write(f"**Required review or action:** {rule.get('required_action', rule.get('label'))}")
            st.write(f"**Control:** {rule.get('control')}")


def render_walkthrough() -> None:
    st.header("Demo Walkthrough")
    steps = [
        "Explain the manual process problem: approvals were scattered across Slack, email, and spreadsheets.",
        "Submit a new AI tool request with owner, vendor, data, use, cost, and justification.",
        "Show how risk scoring translates attributes into a clear score, level, and explanation.",
        "Show triggered policies, required reviews, and practical controls.",
        "Show the audit log as evidence of consistent decisioning.",
        "Show the dashboard for risk, cost, vendor, and data-type monitoring.",
        "Explain how this scales into a real governance operation with routing, integrations, and evidence export.",
    ]
    for i, step in enumerate(steps, start=1):
        st.markdown(f"**Step {i}:** {step}")
    st.subheader("60–90 second talk track")
    st.write(
        "I built this to model how an organization can move from informal AI tool approvals in Slack, email, "
        "or spreadsheets to a repeatable governance workflow. A requester submits the tool, business use case, "
        "vendor, data type, production intent, and expected spend. The system calculates a transparent risk score, "
        "evaluates policy rules, recommends a decision, lists required controls, and writes an audit record. The goal "
        "is not to block innovation. The goal is to let low-risk pilots move quickly while routing higher-risk use cases "
        "through privacy, security, vendor, finance, or leadership review. The dashboard then gives governance leaders a "
        "portfolio view of risk, vendor exposure, sensitive data use, and AI spend."
    )


def main() -> None:
    st.sidebar.title("AI Tool Governance Ops")
    page = st.sidebar.radio(
        "Navigate",
        ["Overview", "Submit AI Tool Request", "Governance Dashboard", "Audit Log", "Policy Rules", "Demo Walkthrough"],
    )
    if page == "Overview":
        render_overview()
    elif page == "Submit AI Tool Request":
        render_submit()
    elif page == "Governance Dashboard":
        render_dashboard()
    elif page == "Audit Log":
        render_audit_log()
    elif page == "Policy Rules":
        render_policy_rules()
    else:
        render_walkthrough()


if __name__ == "__main__":
    main()
