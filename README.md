# Axis Bank Agent Gatekeeper

**Student Name / PGD Enrolment No:** 63936  
**Program:** MBA (Agentic AI Systems Coursework)  
**Project Phase:** Final Submission (Phase 1, Phase 2 & Day 3 Verification)  
**Repository:** [https://github.com/aisfboy5678-dev/Axis-Bank-Agent-Gatekeeper](https://github.com/aisfboy5678-dev/Axis-Bank-Agent-Gatekeeper)

---

## 🏛️ Executive Project Summary

The **Axis Bank Agent Gatekeeper** is an enterprise AI guardrail and policy enforcement layer designed to oversee autonomous AI agents acting on behalf of retail banking customers.

In modern agentic banking workflows, AI agents can initiate tool calls such as balance checks, bill payments, and money transfers. However, unchecked autonomy exposes banks and consumers to severe fraud, hallucination risk, and regulatory violations. The **Gatekeeper** operates as a deterministic middleware checkpoint that intercepts every proposed agent action and evaluates it against **8 Strict Priority Rules** (with an autonomous ceiling of **₹10,000**), categorizing requests into three core governance decisions:

1. 🟢 **ALLOW (Autonomous Execution)**: Safe, read-only inquiries or authorized payments/transfers up to ₹10,000.
2. 🟡 **ASK CUSTOMER (Human-in-the-Loop)**: Value-transferring operations exceeding ₹10,000 or actions lacking standing customer transaction authorization, requiring step-up 2FA/OTP consent.
3. 🔴 **BLOCK (Halted / Prohibited)**: Requests from revoked or unknown agents, actions outside granted customer permissions, or malformed/negative inputs.

> ⚠️ **Educational Simulation Notice:** This prototype is strictly built for academic coursework demonstration. It does not connect to live core banking systems or execute real financial transactions.

---

## 🛡️ The 8-Rule Decision Matrix (Strict Priority Precedence)

Every incoming agent request is evaluated sequentially against these 8 rules. The first matching rule immediately determines the governance outcome:

| Rule ID | Priority | Trigger Condition | Decision | Autonomous Threshold | Banking Policy Rationale |
| :---: | :---: | :--- | :---: | :---: | :--- |
| **R1** | 1 (Highest) | Agent status is **REVOKED** | 🔴 **BLOCK** | N/A | Revoked credentials cannot initiate any action regardless of amount. |
| **R2** | 2 | Agent is **not registered (unknown)** | 🔴 **BLOCK** | N/A | Unrecognized entities are blocked by default to prevent rogue tool calls. |
| **R3** | 3 | Registered active agent requests **View Balance** | 🟢 **ALLOW** | N/A | Read-only inquiry carries zero financial risk; auto-execution approved. |
| **R4** | 4 | Authorised payment/transfer **≤ ₹10,000** | 🟢 **ALLOW** | ₹10,000 | Autonomous execution permitted within authorized threshold. |
| **R5** | 5 | Payment/transfer **> ₹10,000** | 🟡 **ASK CUSTOMER** | ₹10,000 | Exceeds autonomous threshold; step-up 2FA/OTP verification required. |
| **R6** | 6 | Agent tries an **action not permitted by customer** | 🔴 **BLOCK** | N/A | Unauthorized action outside customer's explicit mandate. |
| **R7** | 7 | Customer has **not granted transaction permission** | 🟡 **ASK CUSTOMER** | N/A | Financial action requires explicit customer authorization. |
| **R8** | 8 | **Missing or invalid input** (negative amount, empty fields) | 🔴 **BLOCK** | N/A | Malformed input fails data integrity and safety checks. |

---

## 🎬 6 Compulsory Assignment Test Cases & Live Verification Results

All 6 required assignment test scenarios have been built as **1-click video demonstration presets** in the dashboard and verified in the automated test suite and persistent audit log:

| Test Case | Scenario Description | Customer & Agent Parameters | Action & Amount | Expected Decision | Triggered Rule | Live Verification Status |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: |
| **Test 1** | Known registered agent viewing balance | `Rahul Sharma` / `AxisFinanceBot` | View Balance (₹0) | 🟢 **ALLOW** | **Rule R3** | ✅ Passed & Logged |
| **Test 2** | Unknown unregistered agent transferring ₹2,000 | `Rahul Sharma` / `ShadowBot` | Transfer Money (₹2,000) | 🔴 **BLOCK** | **Rule R2** | ✅ Passed & Logged |
| **Test 3** | Registered agent paying ₹15,000 (above limit) | `Rahul Sharma` / `AxisFinanceBot` | Pay Bill (₹15,000) | 🟡 **ASK CUSTOMER** | **Rule R5** | ✅ Passed & Logged |
| **Test 4** | Registered agent paying ₹5,000 (within limit) | `Rahul Sharma` / `AxisFinanceBot` | Pay Bill (₹5,000) | 🟢 **ALLOW** | **Rule R4** | ✅ Passed & Logged |
| **Test 5** | Revoked agent trying to pay ₹500 | `Amit Verma` / `LegacyHelper` (REVOKED) | Pay Bill (₹500) | 🔴 **BLOCK** | **Rule R1** | ✅ Passed & Logged |
| **Test 6** | Registered agent trying an unauthorised transfer | `Priya Patel` / `BalanceChecker` (Only Balance) | Transfer Money (₹3,000) | 🔴 **BLOCK** | **Rule R6** | ✅ Passed & Logged |

---

## 📁 Project Directory Structure

```text
Axis-Agent-Gatekeeper/
├── app.py                  # Main Streamlit web application & UI
├── test_gatekeeper.py      # Automated unit test suite verifying all 6 test cases + edge cases
├── requirements.txt        # Python library dependencies (Streamlit >= 1.30, Pandas >= 2.0)
├── README.md               # Executive project documentation & user guide
├── PROMPTS.md              # Complete prompt engineering history & human verification log
├── .gitignore              # Ignores virtual environment (.venv/) and cache files
└── data/                   # Persistent storage layer (survives app restarts)
    ├── registered_agents.json # Persistent JSON directory of authorized agents
    └── audit_log.csv          # Persistent CSV ledger of all evaluated transactions
```

---

## 🚀 How to Run the Prototype Application

Follow these simple steps in your terminal to set up and launch the dashboard:

### Step 1: Open Terminal in the Project Directory
```bash
cd "/Users/asifansari/Downloads/Axis-Agent-Gatekeeper "
```

### Step 2: Activate the Python Virtual Environment
```bash
source .venv/bin/activate
```
*(If setting up for the first time on a new computer: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`)*

### Step 3: Start the Streamlit Application
```bash
streamlit run app.py
```

### Step 4: Open in Web Browser
Open your browser and navigate to:
```
http://localhost:8501
```

---

## 🧪 How to Run Automated Unit Tests

To run the automated test suite verifying all 6 compulsory test cases plus additional edge cases (R7 and R8):

```bash
python3 test_gatekeeper.py
```

Expected Output:
```
============================================================
AXIS BANK AGENT GATEKEEPER: VERIFYING 6 COMPULSORY TEST CASES
============================================================
✅ Test 1 Passed: Known registered agent viewing balance -> ALLOW (Rule R3)
✅ Test 2 Passed: Unknown unregistered agent transferring ₹2,000 -> BLOCK (Rule R2)
✅ Test 3 Passed: Registered agent paying ₹15,000 (above limit) -> ASK CUSTOMER (Rule R5)
✅ Test 4 Passed: Registered agent paying ₹5,000 (within limit) -> ALLOW (Rule R4)
✅ Test 5 Passed: Revoked agent trying to pay ₹500 -> BLOCK (Rule R1)
✅ Test 6 Passed: Registered agent trying an unauthorised transfer action -> BLOCK (Rule R6)

============================================================
ADDITIONAL EDGE CASES (R7 & R8):
============================================================
✅ Edge Case Passed: No transaction permission -> ASK CUSTOMER (Rule R7)
✅ Edge Case Passed: Negative amount (-₹500) -> BLOCK (Rule R8)
✅ Edge Case Passed: Empty fields -> BLOCK (Rule R8)

🎉 ALL 6 COMPULSORY TEST CASES + 8 ENGINE RULES VERIFIED WITH 100% SUCCESS!
```

---

## 📊 Compliance Features & Audit Trail
- **Non-Repudiation**: Every decision is stamped with exact date, time, customer name, agent identity, action, amount, decision, rule ID, and policy rationale.
- **CSV Export**: The **Persistent Audit Log** tab provides an instant **"📥 Download Audit Log as CSV"** button for regulatory inspection.
- **One-Click Revocation**: Active agents can be revoked with a single click, recording the exact revocation timestamp and preventing all future tool executions under Rule R1.
