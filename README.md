# AI Tool Governance Ops

A lightweight AI governance operations platform that turns ad hoc AI tool requests into a repeatable approval, risk, privacy, security, cost, and audit workflow.

## The Problem

Many organizations still approve AI tools through spreadsheets, Slack threads, email chains, or informal manager approvals. That approach makes it hard to answer basic governance questions:

- Which AI tools are being used?
- Who owns each tool and business use case?
- Are teams uploading customer data, confidential data, or PII?
- Which tools require privacy, security, finance, vendor risk, or leadership review?
- How much is the organization spending on AI tools?
- What evidence exists for approval and control decisions?

## The Solution

This repo demonstrates a practical governance workflow that is small enough to explain in an interview but realistic enough to resemble a security or program management portfolio project.

It includes:

- **Streamlit intake form** for AI tool requests.
- **Transparent risk scoring** in `risk_scorer.py`.
- **YAML policy rules** in `policies.yaml`.
- **Policy evaluation engine** in `policy_engine.py`.
- **Decision output** with required reviews and controls.
- **JSONL audit logging** in `data/audit_log.jsonl`.
- **Dashboard monitoring** for approvals, risk levels, spend, and recent requests.
- **Sample request data** for demo scenarios.
- **Pytest coverage** for core governance rules.

## How It Balances Innovation and Risk

The workflow does not treat every AI request the same. Low-risk pilots can move quickly with baseline controls, while requests involving PII, customer data, external production vendors, high cost, confidential data, or high aggregate risk are routed to the right review path.

This gives teams a clear way to experiment while giving governance leaders the controls and audit trail needed for responsible adoption.

## Repository Structure

```text
.
├── app.py                         # Streamlit intake form and dashboard
├── audit_logger.py                # JSONL audit logger
├── policy_engine.py               # YAML-driven policy evaluation
├── policies.yaml                  # Review and control rules
├── risk_scorer.py                 # Risk scoring engine
├── data/
│   └── sample_ai_tool_requests.csv
├── docs/
│   ├── control_mapping.md
│   ├── demo_walkthrough.md
│   └── governance_model.md
├── tests/
│   └── test_governance.py
└── requirements.txt
```

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Run Tests

```bash
pytest
```

## Risk Scoring Inputs

The scoring engine considers:

- PII usage
- Customer data usage
- External or open-source vendor type
- Confidential data
- Monthly cost above threshold
- Production use

It returns:

- Risk score
- Risk level: low, medium, high
- Short explanation of risk drivers

## Policy Rules

The default policy file requires:

- Privacy review when PII is used
- Security review when customer data is used
- Finance review when estimated monthly cost is over $500
- Vendor risk review when an external vendor is requested for production
- Leadership approval when the risk level is high

## Example Interview Talking Points

- “This project converts informal AI tool approvals into a structured governance workflow.”
- “The policy rules are in YAML so risk, legal, privacy, finance, and security stakeholders can review them without changing application code.”
- “The scoring model is intentionally explainable rather than black-box.”
- “The dashboard helps identify high-risk requests, review queues, and unmanaged spend.”
- “Audit logging creates evidence for compliance, retrospectives, and leadership reporting.”
- “The workflow supports innovation by allowing low-risk pilots while escalating higher-risk production or sensitive-data use cases.”

## Future Enhancements

- Role-based approval queues
- Authentication and ownership mapping
- Slack or email notifications
- Vendor inventory integration
- Spend alerts
- Policy versioning
- Exportable approval evidence packets
