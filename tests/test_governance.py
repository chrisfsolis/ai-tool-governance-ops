from policy_engine import evaluate_policies
from risk_scorer import calculate_risk


def base_request(**overrides):
    request = {
        "tool_name": "Internal Helper",
        "business_use_case": "Draft internal knowledge base articles",
        "requesting_team": "Operations",
        "owner": "Alex Owner",
        "vendor_type": "internal",
        "data_type": "internal",
        "uses_customer_data": "no",
        "uses_pii": "no",
        "estimated_monthly_usage": 100,
        "estimated_monthly_cost": 100,
        "requested_use": "pilot",
    }
    request.update(overrides)
    return request


def test_low_risk_request_returns_low_risk():
    risk = calculate_risk(base_request())
    assert risk["risk_level"] == "low"
    assert risk["risk_score"] < 30


def test_pii_request_requires_privacy_review():
    request = base_request(uses_pii="yes", data_type="PII")
    policy = evaluate_policies(request, calculate_risk(request))
    assert "Privacy review" in policy["required_reviews"]


def test_customer_data_request_requires_security_review():
    request = base_request(uses_customer_data="yes", data_type="customer data")
    policy = evaluate_policies(request, calculate_risk(request))
    assert "Security review" in policy["required_reviews"]


def test_cost_above_500_requires_finance_review():
    request = base_request(estimated_monthly_cost=501)
    policy = evaluate_policies(request, calculate_risk(request))
    assert "Finance review" in policy["required_reviews"]


def test_high_risk_production_external_tool_requires_leadership_review():
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
    assert "Leadership approval" in policy["required_reviews"]
    assert policy["decision"] == "Not approved until risks are reduced"
