"""Append-only JSONL audit logging for AI governance decisions."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUDIT_LOG_PATH = Path("data/audit_log.jsonl")


def ensure_audit_log(log_path: str | Path = AUDIT_LOG_PATH) -> Path:
    """Create the audit log file and parent directory when missing."""

    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)
    return path


def write_audit_record(
    request: dict[str, Any],
    risk_result: dict[str, Any],
    policy_result: dict[str, Any],
    log_path: str | Path = AUDIT_LOG_PATH,
) -> dict[str, Any]:
    """Write a single audit record and return the persisted object."""

    record = {
        "request_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool_name": request.get("tool_name"),
        "owner": request.get("business_owner") or request.get("owner"),
        "requesting_team": request.get("requesting_team"),
        "vendor_name": request.get("vendor_name"),
        "vendor_type": request.get("vendor_type"),
        "data_type": request.get("data_type"),
        "use_case": request.get("business_use_case"),
        "risk_score": risk_result.get("risk_score"),
        "risk_level": risk_result.get("risk_level"),
        "risk_explanation": risk_result.get("explanation"),
        "triggered_rules": [rule.get("name") or rule.get("label") for rule in policy_result.get("triggered_rules", [])],
        "required_reviews": policy_result.get("required_reviews", []),
        "decision": policy_result.get("decision"),
        "required_controls": policy_result.get("required_controls", []),
        "estimated_monthly_cost": request.get("estimated_monthly_cost"),
        "estimated_monthly_usage": request.get("estimated_monthly_usage"),
    }

    path = ensure_audit_log(log_path)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")
    return record


def read_audit_log(log_path: str | Path = AUDIT_LOG_PATH) -> list[dict[str, Any]]:
    path = ensure_audit_log(log_path)
    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]
