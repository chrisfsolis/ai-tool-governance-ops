"""Fallback command-line demo for environments where Streamlit is unavailable."""

from __future__ import annotations

import csv
from pathlib import Path

from audit_logger import write_audit_record
from policy_engine import evaluate_policies
from risk_scorer import calculate_risk

SAMPLE_DATA_PATH = Path("data/sample_ai_tool_requests.csv")


def load_sample_request() -> dict[str, str]:
    with SAMPLE_DATA_PATH.open("r", encoding="utf-8", newline="") as file:
        return next(csv.DictReader(file))


def main() -> None:
    request = load_sample_request()
    risk_result = calculate_risk(request)
    policy_result = evaluate_policies(request, risk_result)
    audit_record = write_audit_record(request, risk_result, policy_result)

    print("AI Tool Governance Ops CLI Demo")
    print("=" * 32)
    print(f"Tool: {request['tool_name']}")
    print(f"Use case: {request['business_use_case']}")
    print(f"Risk: {risk_result['risk_score']} ({risk_result['risk_level']})")
    print(f"Explanation: {risk_result['explanation']}")
    print(f"Triggered rules: {[rule.get('name') for rule in policy_result['triggered_rules']] or ['None']}")
    print(f"Required reviews: {policy_result['required_reviews'] or ['None']}")
    print(f"Decision: {policy_result['decision']}")
    print("Required controls:")
    for control in policy_result["required_controls"]:
        print(f"- {control}")
    print(f"Audit record written: {audit_record['request_id']}")


if __name__ == "__main__":
    main()
