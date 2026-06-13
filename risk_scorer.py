"""Risk scoring for AI tool governance intake requests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RiskResult:
    """Normalized risk output returned by the scoring engine."""

    risk_score: int
    risk_level: str
    explanation: str


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"yes", "true", "1", "y"}


def _as_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def calculate_risk(request: dict[str, Any], cost_threshold: float = 500) -> dict[str, Any]:
    """Calculate risk score, level, and explanation for an AI tool request.

    Scoring is intentionally transparent so governance, security, and business
    stakeholders can explain why a request is low, medium, or high risk.
    """

    score = 0
    reasons: list[str] = []

    uses_pii = _as_bool(request.get("uses_pii"))
    uses_customer_data = _as_bool(request.get("uses_customer_data"))
    vendor_type = str(request.get("vendor_type", "")).strip().lower()
    data_type = str(request.get("data_type", "")).strip().lower()
    monthly_cost = _as_float(request.get("estimated_monthly_cost"))
    requested_use = str(request.get("requested_use", "")).strip().lower()

    if uses_pii or data_type == "pii":
        score += 35
        reasons.append("uses PII")
    if uses_customer_data or data_type == "customer data":
        score += 25
        reasons.append("uses customer data")
    if vendor_type == "external":
        score += 15
        reasons.append("uses an external vendor")
    elif vendor_type == "open-source":
        score += 10
        reasons.append("uses open-source technology")
    if data_type == "confidential":
        score += 20
        reasons.append("processes confidential data")
    if monthly_cost > cost_threshold:
        score += 10
        reasons.append(f"monthly cost exceeds ${cost_threshold:,.0f}")
    if requested_use == "production":
        score += 15
        reasons.append("requested for production use")

    if score >= 65:
        level = "high"
    elif score >= 30:
        level = "medium"
    else:
        level = "low"

    explanation = "Risk driven by " + ", ".join(reasons) + "." if reasons else "Low inherent risk based on submitted attributes."
    return RiskResult(score, level, explanation).__dict__
