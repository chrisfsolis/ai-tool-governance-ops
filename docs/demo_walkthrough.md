# Demo Walkthrough

## 1. Open the App

Run `streamlit run app.py` and open the local Streamlit URL.

## 2. Submit a Low-Risk Pilot

Use an internal writing assistant with internal data, no customer data, no PII, low cost, and pilot use. The app should return a low risk score and **Approved for pilot** with baseline controls.

## 3. Submit a Sensitive External Tool

Use an external production customer support tool that processes customer data or PII and costs more than $500 per month. The app should require privacy, security, finance, vendor risk, and leadership review depending on the exact inputs.

## 4. Review the Dashboard

Switch to the dashboard tab to show:

- Total tools reviewed
- Approved tools
- Requests still requiring review
- High-risk requests
- Estimated monthly AI spend
- Requests by risk level
- Recent audit log entries

## 5. Interview Talking Points

- The policy engine is deliberately transparent and YAML-driven so governance stakeholders can reason about the workflow.
- Audit logging creates evidence for reviews, retrospectives, and compliance requests.
- Low-risk pilots remain fast while production, sensitive-data, vendor, and high-cost use cases get escalated.
