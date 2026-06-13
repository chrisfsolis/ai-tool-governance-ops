import json

from audit_logger import read_audit_log, write_audit_record
from policy_engine import evaluate_policies
from risk_scorer import calculate_risk


def base_request(**overrides):
    request = {
        "tool_name": "Internal Helper",
        "business_use_case": "Draft public FAQ copy",
        "requesting_team": "Operations",
        "business_owner": "Alex Owner",
        "owner": "Alex Owner",
        "vendor_name": "Internal Platform",
        "vendor_type": "internal",
        "data_type": "public",
        "uses_customer_data": "no",
        "uses_pii": "no",
        "estimated_monthly_usage": 100,
        "estimated_monthly_cost": 100,
        "requested_use": "pilot",
    }
    request.update(overrides)
    return request


def test_low_risk_public_data_pilot_returns_low_risk():
    risk = calculate_risk(base_request())
    policy = evaluate_policies(base_request(), risk)
    assert risk["risk_level"] == "low"
    assert risk["risk_score"] < 30
    assert policy["decision"] == "Approved for pilot"


def test_pii_triggers_privacy_review():
    request = base_request(uses_pii="yes", data_type="PII")
    policy = evaluate_policies(request, calculate_risk(request))
    assert "Privacy review" in policy["required_reviews"]


def test_customer_data_triggers_security_review():
    request = base_request(uses_customer_data="yes", data_type="customer data")
    policy = evaluate_policies(request, calculate_risk(request))
    assert "Security review" in policy["required_reviews"]


def test_external_production_use_triggers_vendor_risk_review():
    request = base_request(vendor_type="external", requested_use="production")
    policy = evaluate_policies(request, calculate_risk(request))
    assert "Vendor risk review" in policy["required_reviews"]


def test_cost_over_threshold_triggers_finance_review():
    request = base_request(estimated_monthly_cost=501)
    policy = evaluate_policies(request, calculate_risk(request))
    assert "Finance review" in policy["required_reviews"]


def test_high_risk_requests_trigger_leadership_review():
    request = base_request(
        vendor_type="external",
        data_type="PII",
        uses_customer_data="yes",
        uses_pii="yes",
        estimated_monthly_cost=1200,
        requested_use="production",
    )
    risk = calculate_risk(request)
    policy = evaluate_policies(request, risk)
    assert risk["risk_level"] == "high"
    assert "Leadership review" in policy["required_reviews"]
    assert policy["decision"] == "Not approved until risks are reduced"


def test_audit_logger_writes_valid_jsonl(tmp_path):
    path = tmp_path / "audit_log.jsonl"
    request = base_request()
    risk = calculate_risk(request)
    policy = evaluate_policies(request, risk)
    record = write_audit_record(request, risk, policy, path)
    line = path.read_text(encoding="utf-8").strip()
    parsed = json.loads(line)
    assert parsed["request_id"] == record["request_id"]
    assert parsed["decision"] == "Approved for pilot"


def test_missing_audit_log_file_is_created_automatically(tmp_path):
    path = tmp_path / "missing" / "audit_log.jsonl"
    assert read_audit_log(path) == []
    assert path.exists()


def test_policy_engine_returns_expected_triggered_rules():
    request = base_request(uses_pii="yes", estimated_monthly_cost=900)
    policy = evaluate_policies(request, calculate_risk(request))
    rule_ids = {rule["id"] for rule in policy["triggered_rules"]}
    assert {"privacy_review", "finance_review"}.issubset(rule_ids)
