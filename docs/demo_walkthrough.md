# Demo Walkthrough

## Step 1: Explain the manual process problem
Many AI tool approvals start in Slack, email, or spreadsheets. That creates inconsistent review, unclear ownership, limited auditability, and weak visibility into risk and spend.

## Step 2: Submit a new AI tool request
Use the Streamlit intake page to capture the tool name, use case, team, business owner, vendor, data type, PII/customer data flags, pilot or production use, expected usage, cost, and justification.

## Step 3: Show how risk scoring works
The risk model assigns points for sensitive data, external vendors, production use, confidential data, and high spend. The result is a risk score, risk level, and business-readable explanation.

## Step 4: Show triggered policies and required reviews
The policy engine maps request attributes to review paths such as privacy, security, vendor risk, finance, and leadership review. It also displays required controls.

## Step 5: Show the audit log
Every submitted decision writes an append-only JSONL audit record with timestamp, request ID, owner, risk level, decision, reviews, controls, and cost.

## Step 6: Show the dashboard
The dashboard summarizes total reviewed requests, approvals, requests needing additional review, high-risk requests, spend, average risk score, risk levels, vendor types, data types, and top risk/cost tools.

## Step 7: Explain how this scales
A production version could add SSO/RBAC, Jira or ServiceNow routing, vendor risk APIs, OpenAI or Azure OpenAI usage tracking, SOC 2 / ISO 27001 evidence export, NIST AI RMF / ISO 42001 mappings, Slack notifications, exception workflows, and a database backend.

## 60–90 second talk track
“I built this to model how an organization can move from informal AI tool approvals in Slack, email, or spreadsheets to a repeatable governance workflow. A requester submits a structured intake form with owner, vendor, data, use, and spend. The workflow calculates risk, evaluates policy rules, recommends a decision, lists controls, and writes an audit log. The goal is not to block innovation. The goal is to allow low-risk experimentation to move quickly while routing higher-risk use cases through privacy, security, vendor, finance, or leadership review. The dashboard then gives governance leaders visibility into AI risk, vendor exposure, sensitive data use, and spend.”
