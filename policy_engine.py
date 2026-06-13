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
    """Return required reviews, controls, and recommended decision."""

    policies = load_policies(policy_path)
    required_reviews: list[str] = []
    required_controls = list(policies.get("baseline_controls", []))

    for rule in policies.get("reviews", []):
        if _matches(rule.get("when", {}), request, risk_result):
            required_reviews.append(rule["label"])
            required_controls.append(rule["control"])

    decision = _recommend_decision(request, risk_result, required_reviews, policies.get("decisions", {}))
    return {
        "required_reviews": required_reviews,
        "decision": decision,
        "required_controls": list(dict.fromkeys(required_controls)),
    }


def _recommend_decision(
    request: dict[str, Any],
    risk_result: dict[str, Any],
    required_reviews: list[str],
    decisions: dict[str, str],
) -> str:
    if risk_result.get("risk_level") == "high":
        return decisions.get("high", "Not approved until risks are reduced")
    if "Privacy review" in required_reviews:
        return decisions.get("privacy", "Requires privacy review")
    if "Security review" in required_reviews:
        return decisions.get("security", "Requires security review")
    if "Finance review" in required_reviews:
        return decisions.get("finance", "Requires finance review")
    if str(request.get("requested_use", "")).lower() == "pilot":
        return decisions.get("low_pilot", "Approved for pilot")
    return decisions.get("low_production", "Approved with controls")
