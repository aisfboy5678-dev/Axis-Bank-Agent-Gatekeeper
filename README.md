# Axis Bank Agent Gatekeeper

**Student Name / PGD Enrolment No:** 63936  
**Program:** MBA (Agentic AI Coursework)  
**Project Phase:** Phase 2 — Full Governance Engine, Agent Lifecycle & Persistent Audit Log

---

## 🏛️ Project Overview
The **Axis Bank Agent Gatekeeper** is an enterprise AI guardrail system designed to regulate autonomous AI agents interacting with core banking services. 

When an AI agent acts on behalf of a customer, the Gatekeeper intercepts every proposed transaction and evaluates it through **8 Strict Priority Rules** (with an autonomous execution ceiling of **₹10,000**), categorizing the request into one of three governance outcomes:

1. 🟢 **ALLOW (Autonomous Execution)**: Safe, read-only requests or authorised transfers up to ₹10,000.
2. 🟡 **ASK CUSTOMER (Human-in-the-Loop)**: Value-transferring operations exceeding ₹10,000 or actions where standing transaction consent has not been granted.
3. 🔴 **BLOCK (Halted / Prohibited)**: Requests from revoked or unknown agents, unauthorized actions outside customer permissions, or invalid/malformed inputs.

> ⚠️ **Educational Simulation Only:** This project is strictly for academic purposes and does not connect to live banking databases or execute real financial transactions.

---

## 🛡️ The 8-Rule Decision Matrix (Strict Priority Precedence)

| Rule ID | Trigger Condition | Decision | Priority | Banking Policy Rationale |
| :--- | :--- | :---: | :---: | :--- |
| **R1** | Agent status is **REVOKED** | 🔴 **BLOCK** | 1 (Highest) | Revoked agents cannot initiate any action. |
| **R2** | Agent is **not registered (unknown)** | 🔴 **BLOCK** | 2 | Unrecognized entities are blocked by default. |
| **R3** | Registered active agent requests **View Balance** | 🟢 **ALLOW** | 3 | Read-only inquiry carries zero financial loss risk. |
| **R4** | Authorised payment/transfer **≤ ₹10,000** | 🟢 **ALLOW** | 4 | Autonomous execution allowed within ₹10,000 threshold. |
| **R5** | Payment/transfer **> ₹10,000** | 🟡 **ASK CUSTOMER** | 5 | Exceeds autonomous threshold; 2FA/OTP required. |
| **R6** | Agent tries an **action not permitted by customer** | 🔴 **BLOCK** | 6 | Action is outside the customer's granted mandate. |
| **R7** | Customer has **not granted transaction permission** | 🟡 **ASK CUSTOMER** | 7 | Financial action requires explicit customer authorization. |
| **R8** | **Missing or invalid input** (negative amount, empty fields) | 🔴 **BLOCK** | 8 | Request fails data integrity checks. |

---

## 📁 Project Directory Structure
```text
Axis-Agent-Gatekeeper/
├── app.py                  # Full Streamlit Phase 2 dashboard
├── test_gatekeeper.py      # Automated unit test suite verifying all 8 rules
├── requirements.txt        # Dependencies (Streamlit, Pandas)
├── README.md               # Complete architecture & user guide
├── .gitignore              # Ignores cache & environment files
└── data/                   # Persistent storage directory
    ├── registered_agents.json # Persistent JSON store of registered agents
    └── audit_log.csv          # Persistent CSV ledger of all evaluations
```

---

## 🚀 How to Run the Application

In your Terminal, from the project directory:

```bash
# 1. Activate Virtual Environment
source .venv/bin/activate

# 2. Run the Streamlit Dashboard
streamlit run app.py
```

Open your browser to: **`http://localhost:8501`**

---

## 🧪 Testing the 8 Rules

On the **Gatekeeper Request Simulator** tab, click any of the 8 quick preset buttons at the top:
- **Test R1:** Revoked agent `LegacyHelper` → 🔴 **BLOCK**
- **Test R2:** Unknown agent `HackerBot` → 🔴 **BLOCK**
- **Test R3:** Active agent `AxisFinanceBot` viewing balance → 🟢 **ALLOW**
- **Test R4:** Transfer ₹6,500 (≤ ₹10,000) → 🟢 **ALLOW**
- **Test R5:** Transfer ₹25,000 (> ₹10,000) → 🟡 **ASK CUSTOMER**
- **Test R6:** Agent `BalanceChecker` attempting transfer without permission → 🔴 **BLOCK**
- **Test R7:** Agent with transaction permission toggled off → 🟡 **ASK CUSTOMER**
- **Test R8:** Transfer with negative amount (-₹500) or blank name → 🔴 **BLOCK**

You can also run the automated unit test suite from your terminal:
```bash
python3 test_gatekeeper.py
```
*(All 8 rules pass with 100% accuracy).*
