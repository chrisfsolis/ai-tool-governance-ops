# AI Tool Governance Ops

## Project Overview
AI Tool Governance Ops is an interview-ready demo of a scalable AI tool approval workflow. It replaces scattered Slack, email, and spreadsheet approvals with structured intake, transparent risk scoring, policy-based review routing, cost controls, audit logging, and dashboard reporting.

## Problem
Many organizations adopt AI tools faster than governance teams can review them. Manual approvals create inconsistent decisions, weak audit evidence, unclear owners, unmanaged spend, and privacy/security blind spots.

## Solution
This project models a lightweight operating workflow for AI governance:
1. Capture a standardized AI tool request.
2. Calculate a transparent risk score.
3. Trigger privacy, security, vendor, finance, or leadership reviews from policy rules.
4. Recommend a practical decision and controls.
5. Write an audit record.
6. Monitor the portfolio through a governance dashboard.

## Why This Matters
The goal is not to block innovation. The goal is to let low-risk AI experimentation move quickly while routing sensitive, expensive, external, or production use cases through the right review path.

## Architecture
- `app.py` - Streamlit multi-page demo app.
- `risk_scorer.py` - Transparent risk scoring model.
- `policy_engine.py` - YAML-driven policy evaluation and decision logic.
- `audit_logger.py` - Append-only JSONL audit logging.
- `policies.yaml` - Review rules, required actions, and baseline controls.
- `data/sample_ai_tool_requests.csv` - Realistic request portfolio for dashboard reporting.
- `demo_cli.py` - Streamlit-free fallback demo.
- `tests/test_governance.py` - Regression tests for scoring, policies, and audit logging.

## Governance Workflow
1. Requester submits tool details, owner, vendor, data type, usage, cost, and justification.
2. Risk scoring evaluates PII, customer data, confidential data, vendor type, production use, and spend.
3. Policy rules trigger required reviews and controls.
4. The decision is displayed as approved for pilot, approved with controls, requires additional review, or not approved until risks are reduced.
5. The decision is written to the audit log.
6. The dashboard summarizes reviewed requests, risk distribution, vendor exposure, data types, spend, and highest-risk/highest-cost tools.

## Risk Scoring Model
The risk model intentionally favors explainability over complexity. It adds points for sensitive factors:
- PII
- Customer data
- Confidential data
- External or open-source vendors
- Production use
- Monthly cost above threshold

Risk levels are low, medium, or high, and every score includes a plain-language explanation.

## Policy Rules
`policies.yaml` contains stakeholder-readable rules for:
- Privacy review when PII is used.
- Security review when customer data is used.
- Finance review when spend exceeds the threshold.
- Vendor risk review for external production use.
- Leadership review for high-risk requests.

## Audit Logging
`audit_logger.py` writes append-only JSONL records to `data/audit_log.jsonl`. The file is automatically created if missing. Each record includes request ID, timestamp, owner, risk level, decision, required reviews, required controls, and estimated monthly cost.

## Dashboard
The Streamlit dashboard combines sample requests and audit log entries to show:
- Total reviewed requests
- Approved for pilot
- Approved with controls
- Requires additional review
- High-risk requests
- Estimated monthly AI spend
- Average risk score
- Requests by risk level, vendor type, and data type
- Top 5 highest-risk tools
- Top 5 highest-cost tools

## How to Run
```bash
make install
make run
```

Equivalent commands:
```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## CLI Demo Backup
If Streamlit cannot be installed in a restricted environment, run:
```bash
python demo_cli.py
```

The CLI loads a sample request, calculates risk, evaluates policies, prints the decision and controls, and writes an audit log record.

## Testing
```bash
make test
```

Equivalent command:
```bash
pytest -q
```

Compile check:
```bash
python -m py_compile app.py audit_logger.py policy_engine.py risk_scorer.py demo_cli.py
```

## Demo Walkthrough
1. Start on the Overview page and explain the governance problem.
2. Submit a realistic AI tool request.
3. Walk through the risk score and explanation.
4. Show triggered policy rules, required reviews, and controls.
5. Open the Audit Log page to show evidence capture.
6. Open the Governance Dashboard to show portfolio monitoring.
7. Explain how the same pattern can scale with workflow integrations, role-based access, vendor APIs, and compliance evidence exports.

## Interview Talk Track
“I built this to model how an organization can move from informal AI tool approvals in Slack, email, or spreadsheets to a repeatable governance workflow. The goal is not to block innovation. The goal is to allow low-risk experimentation to move quickly while routing higher-risk use cases through privacy, security, vendor, finance, or leadership review.”

## Future Enhancements
- SSO/RBAC
- Vendor risk API integration
- Jira/ServiceNow approval routing
- Azure OpenAI or OpenAI usage tracking
- Cost dashboards
- SOC 2 / ISO 27001 evidence export
- NIST AI RMF / ISO 42001 control mapping
- Exception review workflow
- Slack approval notifications
- Database backend
