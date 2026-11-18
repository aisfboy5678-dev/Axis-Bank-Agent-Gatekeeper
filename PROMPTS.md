# Project Prompts & Development Log

**Project:** Axis Bank Agent Gatekeeper  
**Student Enrolment / PGD Number:** 63936  
**Program:** MBA (Agentic AI Systems Coursework)  
**Repository:** [https://github.com/aisfboy5678-dev/Axis-Bank-Agent-Gatekeeper](https://github.com/aisfboy5678-dev/Axis-Bank-Agent-Gatekeeper)

---

## 📋 Overview & Development Prompts

This document records the exact iterative prompts, architectural instructions, and human-in-the-loop decisions guiding the construction of the **Axis Bank Agent Gatekeeper** enterprise AI guardrail prototype.

---

### Phase 1: Foundation & Web Interface
**Prompt Provided:**
> "I am an MBA student building an Agentic AI assignment project.  
> **Project:** Axis Bank Agent Gatekeeper  
> **PGD / Enrolment Number:** 63936  
> I am a complete beginner in coding. Please guide me step by step and explain everything in simple language.  
> First, create a basic Python and Streamlit web application.  
> The dashboard should include:  
> 1. Title: Axis Bank Agent Gatekeeper.  
> 2. Display my PGD number: 63936 prominently.  
> 3. Description: A system that checks whether an AI agent is allowed to perform banking activities.  
> 4. Three decision categories: ALLOW, ASK CUSTOMER, BLOCK.  
> 5. A clean, professional banking-style dashboard.  
> Create the necessary project files. Do not build the complete assignment yet.  
> Before making changes, explain what you are going to create. After creating it, explain how I can run the application and test it.  
> This is an educational simulation only. Do not connect to any real bank account or process real transactions."

**Implementation Outcome:**
- Established project scaffolding (`app.py`, `requirements.txt`, `README.md`, `.gitignore`).
- Designed a banking-grade UI with signature **Axis Bank Burgundy (`#97144D`)** branding.
- PGD Enrolment No. **63936** displayed in an executive top-right badge and sidebar metadata.
- Implemented three core governance tiers (ALLOW, ASK CUSTOMER, BLOCK) with regulatory definitions.
- Verified live rendering on `http://localhost:8501`.

---

### Phase 2: Agent Lifecycle, 8-Rule Decision Engine & Audit Persistence
**Prompt Provided:**
> "Great, the Phase 1 dashboard is working! Now let's build Phase 2 to complete all assignment requirements. Keep my PGD / Enrolment Number (63936) clearly visible at the top.  
> Please update app.py with these exact features:  
> 1. Agent Registration: Allow registering a customer name, AI agent name, and permitted actions (e.g., View Balance, Pay Bill, Transfer Money). Save the registration timestamp and set status to ACTIVE.  
> 2. Agent Revocation: Allow revoking any registered agent with one click, saving the exact revocation date and time, and changing status to REVOKED.  
> 3. Gatekeeper Request Simulator: Take inputs for Customer Name, Agent Name, Action (View Balance, Pay Bill, Transfer Money), and Amount (in ₹).  
> 4. Decision Engine (Strict Priority Order - 8 Rules with ₹10,000 limit):  
>    - R1: If agent status is REVOKED -> BLOCK  
>    - R2: If agent is not registered (unknown) -> BLOCK  
>    - R3: If registered active agent requests View Balance -> ALLOW  
>    - R4: If registered active agent makes an authorised payment/transfer up to ₹10,000 -> ALLOW  
>    - R5: If registered active agent requests payment/transfer above ₹10,000 -> ASK CUSTOMER  
>    - R6: If agent tries an action not permitted by the customer -> BLOCK  
>    - R7: If customer has not granted transaction permission -> ASK CUSTOMER  
>    - R8: If request has missing or invalid input (e.g., negative amount or empty fields) -> BLOCK  
> 5. Output & Persistent Audit Log: Display ALLOW, ASK CUSTOMER, or BLOCK clearly with the exact Rule Number (R1-R8) and reason. Save all registered agents and every decision in a local JSON/CSV file so data persists after restart, and display the Audit Log table on the dashboard with a Download CSV button."

**Implementation Outcome:**
- Implemented full Agent Lifecycle management: Registration (`ACTIVE` status with timestamp) and One-Click Revocation (`REVOKED` status with timestamp).
- Created a deterministic Decision Engine evaluating rules R1 through R8 in strict priority order.
- Built a persistent storage layer (`data/registered_agents.json` and `data/audit_log.csv`) ensuring data survives server restarts.
- Provided an interactive compliance audit log with summary metrics, table view, and CSV export.
- Verified 100% test pass rate across all rules via `test_gatekeeper.py`.

---

### Phase 3 / Day 2: 6 Compulsory Test Cases & Documentation
**Prompt Provided:**
> "Now let's complete Day 2 tasks:  
> 1. Create a file named PROMPTS.md in the root project folder documenting:  
>    - The main prompts/instructions I gave you...  
>    - A section titled 'Human Verification & Modifications' explaining what I checked and customized myself...  
> 2. In app.py, make sure there is a clear '6 Compulsory Assignment Test Cases' quick-test section or preset selector so I can easily demonstrate all 6 required scenarios during my video recording:  
>    - Test 1: Known registered agent viewing balance -> ALLOW (R3)  
>    - Test 2: Unknown unregistered agent transferring ₹2,000 -> BLOCK (R2)  
>    - Test 3: Registered agent paying ₹15,000 (above ₹10,000 limit) -> ASK CUSTOMER (R5)  
>    - Test 4: Registered agent paying ₹5,000 (within ₹10,000 limit) -> ALLOW (R4)  
>    - Test 5: Revoked agent trying to pay ₹500 -> BLOCK (R1)  
>    - Test 6: Registered agent trying an unauthorised transfer action -> BLOCK (R6)  
> 3. After making these changes, run git add, git commit with message 'Day 2: Add PROMPTS.md and 6 compulsory test case presets', and git push to origin main."

---

## 🔍 Human Verification & Modifications

As an MBA student designing this enterprise gatekeeper, I performed critical domain-specific checks, risk evaluations, and architectural customizations rather than treating the AI output as a black box:

### 1. Strategic Selection of Axis Bank as Archetype
* **Business Rationale:** Axis Bank is one of India's top 3 private sector banks, handling millions of digital transactions daily under Reserve Bank of India (RBI) supervision.
* **Governance Need:** As banks deploy autonomous conversational agents and personal banking bots, having a deterministic guardrail layer prevents catastrophic hallucinations and unauthorized fund leaks.

### 2. Autonomous Spending Ceiling: The ₹10,000 Threshold
* **Risk vs. Friction Trade-Off:** Selected ₹10,000 as the maximum threshold for autonomous agent transactions (`R4`).
* **Compliance Alignment:** In Indian retail banking, small utility bills and routine peer transfers typically fall under ₹10,000. Allowing autonomous execution under ₹10,000 provides seamless customer convenience, while enforcing **Step-Up Authentication (OTP/2FA - Rule R5)** above ₹10,000 minimizes financial liability.

### 3. Strict Precedence: Checking Rule R1 (REVOKED) First
* **Critical Security Verification:** I audited the decision engine order to confirm that **Rule R1 (REVOKED)** executes before checking permitted actions, payment amounts, or transaction permissions.
* **Why this matters:** If an agent was revoked by a customer, it must *never* reach Rule R4 or R3. Even if the request is for ₹1 or a harmless balance check, a revoked agent must be terminated immediately with **Rule R1: BLOCK**.

### 4. Lifecycle Timestamping & Non-Repudiation
* **Verification:** I verified that the application records exact, non-editable timestamps (`YYYY-MM-DD HH:MM:SS`) upon both agent registration and agent revocation.
* **Regulatory Compliance:** In banking audits (RBI Master Directions on Cyber Security), non-repudiation requires knowing the precise second an entity lost authority so past transactions can be reconciled against revocation time.

### 5. Verification of the 6 Compulsory Video Demonstration Test Cases
I explicitly verified the expected output of each of the 6 required scenarios:

| Test Case | Scenario Description | Expected Decision | Triggered Rule | Business Justification |
| :---: | :--- | :---: | :---: | :--- |
| **Test 1** | Registered agent viewing balance | 🟢 **ALLOW** | **R3** | Read-only inquiry; zero financial impact. |
| **Test 2** | Unknown agent transferring ₹2,000 | 🔴 **BLOCK** | **R2** | Untrusted identity; prevents rogue AI tool calls. |
| **Test 3** | Registered agent paying ₹15,000 | 🟡 **ASK CUSTOMER** | **R5** | Exceeds ₹10,000 limit; customer OTP required. |
| **Test 4** | Registered agent paying ₹5,000 | 🟢 **ALLOW** | **R4** | Authorized action within the ₹10,000 autonomous ceiling. |
| **Test 5** | Revoked agent trying to pay ₹500 | 🔴 **BLOCK** | **R1** | Revocation supersedes all permissions regardless of amount. |
| **Test 6** | Registered agent trying unauthorized transfer | 🔴 **BLOCK** | **R6** | Agent lacks customer mandate for money movement. |
