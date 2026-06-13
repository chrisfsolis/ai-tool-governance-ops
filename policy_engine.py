"""Policy evaluation engine for AI tool governance requests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import json

DEFAULT_POLICY_PATH = Path(__file__).with_name("policies.yaml")


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"yes", "true", "1", "y"}


def _as_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def load_policies(policy_path: str | Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    """Load policy rules from YAML."""

    with Path(policy_path).open("r", encoding="utf-8") as file:
        return json.load(file)


def _matches(condition: dict[str, Any], request: dict[str, Any], risk_result: dict[str, Any]) -> bool:
    for key, expected in condition.items():
        if key == "estimated_monthly_cost_gt":
            if _as_float(request.get("estimated_monthly_cost")) <= float(expected):
                return False
        elif key == "risk_level":
            if str(risk_result.get("risk_level", "")).lower() != str(expected).lower():
                return False
        elif isinstance(expected, bool):
            if _as_bool(request.get(key)) != expected:
                return False
        else:
            if str(request.get(key, "")).strip().lower() != str(expected).lower():
                return False
    return True


def evaluate_policies(
    request: dict[str, Any],
    risk_result: dict[str, Any],
    policy_path: str | Path = DEFAULT_POLICY_PATH,
) -> dict[str, Any]:
    """Return triggered rules, required reviews, controls, and recommended decision."""

    policies = load_policies(policy_path)
    required_reviews: list[str] = []
    triggered_rules: list[dict[str, Any]] = []
    required_controls = list(policies.get("baseline_controls", []))

    for rule in policies.get("reviews", []):
        if _matches(rule.get("when", {}), request, risk_result):
            required_reviews.append(rule["label"])
            triggered_rules.append(rule)
            required_controls.append(rule["control"])

    required_controls.extend(_contextual_controls(request, risk_result))
    decision = _recommend_decision(request, risk_result, required_reviews, policies.get("decisions", {}))
    return {
        "triggered_rules": triggered_rules,
        "required_reviews": list(dict.fromkeys(required_reviews)),
        "decision": decision,
        "required_controls": list(dict.fromkeys(required_controls)),
    }


def _contextual_controls(request: dict[str, Any], risk_result: dict[str, Any]) -> list[str]:
    controls: list[str] = []
    if _as_bool(request.get("uses_pii")) or str(request.get("data_type", "")).lower() == "pii":
        controls.append("Restrict use to pilot until privacy review is complete.")
    if str(request.get("vendor_type", "")).lower() == "external":
        controls.append("Use approved enterprise account only.")
    if str(request.get("requested_use", "")).lower() == "production":
        controls.append("Complete vendor security review before production deployment.")
    if _as_float(request.get("estimated_monthly_cost")) > 500:
        controls.append("Review monthly spend after 30 days.")
    if risk_result.get("risk_level") == "high":
        controls.append("Require human review before external use of AI-generated outputs.")
    return controls


def _recommend_decision(
    request: dict[str, Any],
    risk_result: dict[str, Any],
    required_reviews: list[str],
    decisions: dict[str, str],
) -> str:
    sensitive_factor_count = sum(
        [
            _as_bool(request.get("uses_pii")) or str(request.get("data_type", "")).lower() == "pii",
            _as_bool(request.get("uses_customer_data")) or str(request.get("data_type", "")).lower() == "customer data",
            str(request.get("vendor_type", "")).lower() == "external",
            str(request.get("requested_use", "")).lower() == "production",
            _as_float(request.get("estimated_monthly_cost")) > 500,
        ]
    )
    risk_level = str(risk_result.get("risk_level", "")).lower()
    external_production = (
        str(request.get("vendor_type", "")).lower() == "external"
        and str(request.get("requested_use", "")).lower() == "production"
    )

    if risk_level == "high" and sensitive_factor_count >= 3:
        return decisions.get("high", "Not approved until risks are reduced")
    if risk_level == "high" or _as_bool(request.get("uses_pii")) or _as_bool(request.get("uses_customer_data")) or external_production:
        return decisions.get("additional_review", "Requires additional review")
    if risk_level == "medium":
        return decisions.get("medium", "Approved with controls")
    if required_reviews:
        return decisions.get("additional_review", "Requires additional review")
    if str(request.get("requested_use", "")).lower() == "pilot":
        return decisions.get("low_pilot", "Approved for pilot")
    return decisions.get("low_production", "Approved with controls")
