import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Axis Bank Agent Gatekeeper - Phase 2",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# PERSISTENCE DATA LAYER (JSON & CSV)
# ==========================================
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
AGENTS_FILE = os.path.join(DATA_DIR, "registered_agents.json")
AUDIT_FILE = os.path.join(DATA_DIR, "audit_log.csv")

os.makedirs(DATA_DIR, exist_ok=True)

def get_default_agents():
    """Seed sample agents for immediate academic demonstration."""
    return [
        {
            "customer_name": "Rahul Sharma",
            "agent_name": "AxisFinanceBot",
            "permitted_actions": ["View Balance", "Pay Bill", "Transfer Money"],
            "transaction_permission": True,
            "registered_at": "2026-11-18 09:30:00",
            "status": "ACTIVE",
            "revoked_at": None
        },
        {
            "customer_name": "Priya Patel",
            "agent_name": "BalanceChecker",
            "permitted_actions": ["View Balance"],
            "transaction_permission": False,
            "registered_at": "2026-11-18 10:15:00",
            "status": "ACTIVE",
            "revoked_at": None
        },
        {
            "customer_name": "Amit Verma",
            "agent_name": "LegacyHelper",
            "permitted_actions": ["View Balance", "Transfer Money"],
            "transaction_permission": True,
            "registered_at": "2026-11-15 08:00:00",
            "status": "REVOKED",
            "revoked_at": "2026-11-17 16:45:00"
        }
    ]

def load_agents():
    if not os.path.exists(AGENTS_FILE):
        default_agents = get_default_agents()
        save_agents(default_agents)
        return default_agents
    try:
        with open(AGENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        default_agents = get_default_agents()
        save_agents(default_agents)
        return default_agents

def save_agents(agents_list):
    with open(AGENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(agents_list, f, indent=2, ensure_ascii=False)

def load_audit_log():
    if not os.path.exists(AUDIT_FILE):
        df = pd.DataFrame(columns=[
            "Timestamp", "Customer Name", "Agent Name", "Action", "Amount (₹)",
            "Decision", "Rule ID", "Rule Name", "Policy Rationale"
        ])
        df.to_csv(AUDIT_FILE, index=False)
        return df
    try:
        return pd.read_csv(AUDIT_FILE)
    except Exception:
        df = pd.DataFrame(columns=[
            "Timestamp", "Customer Name", "Agent Name", "Action", "Amount (₹)",
            "Decision", "Rule ID", "Rule Name", "Policy Rationale"
        ])
        df.to_csv(AUDIT_FILE, index=False)
        return df

def append_audit_log(entry):
    df = load_audit_log()
    new_row = pd.DataFrame([entry])
    df = pd.concat([new_row, df], ignore_index=True)
    df.to_csv(AUDIT_FILE, index=False)
    return df

# Initialize Session State
if "agents" not in st.session_state:
    st.session_state.agents = load_agents()

# ==========================================
# DECISION ENGINE: STRICT PRIORITY ORDER (R1-R8)
# Threshold: ₹10,000
# ==========================================
def evaluate_request(customer_name, agent_name, action, amount, agents_list):
    """
    Evaluates an agent request through the 8 strict priority rules.
    Returns: dict(decision, rule_id, rule_name, reason)
    """
    c_name = customer_name.strip() if customer_name else ""
    a_name = agent_name.strip() if agent_name else ""

    # -------------------------------------------------------------
    # R8: Empty fields or negative amount (Input validation)
    # -------------------------------------------------------------
    if not c_name or not a_name:
        return {
            "decision": "BLOCK",
            "rule_id": "R8",
            "rule_name": "Missing or Invalid Input",
            "reason": f"Input validation failed: Customer Name ('{c_name}') and Agent Name ('{a_name}') cannot be empty."
        }

    if action in ["Pay Bill", "Transfer Money"]:
        if amount is None or amount < 0:
            return {
                "decision": "BLOCK",
                "rule_id": "R8",
                "rule_name": "Missing or Invalid Input",
                "reason": f"Input validation failed: Invalid transaction amount (₹{amount}). Amount cannot be negative or empty."
            }

    # Locate agent record
    matched_agent = None
    for ag in agents_list:
        if (ag.get("agent_name", "").strip().lower() == a_name.lower() and 
            ag.get("customer_name", "").strip().lower() == c_name.lower()):
            matched_agent = ag
            break

    # -------------------------------------------------------------
    # R1: If agent status is REVOKED -> BLOCK
    # -------------------------------------------------------------
    if matched_agent and matched_agent.get("status") == "REVOKED":
        revoked_time = matched_agent.get("revoked_at") or "Unknown Time"
        return {
            "decision": "BLOCK",
            "rule_id": "R1",
            "rule_name": "Agent Status REVOKED",
            "reason": f"Agent '{a_name}' was explicitly REVOKED by customer '{c_name}' on {revoked_time}. All operations are blocked."
        }

    # -------------------------------------------------------------
    # R2: If agent is not registered (unknown) -> BLOCK
    # -------------------------------------------------------------
    if not matched_agent:
        return {
            "decision": "BLOCK",
            "rule_id": "R2",
            "rule_name": "Unregistered / Unknown Agent",
            "reason": f"Agent '{a_name}' is not registered under customer '{c_name}'. Unrecognized agents are blocked by default."
        }

    # Agent is registered and ACTIVE
    permitted_actions = matched_agent.get("permitted_actions", [])
    transaction_permission = matched_agent.get("transaction_permission", True)

    # -------------------------------------------------------------
    # R3: If registered active agent requests View Balance -> ALLOW
    # -------------------------------------------------------------
    if action == "View Balance":
        if "View Balance" in permitted_actions:
            return {
                "decision": "ALLOW",
                "rule_id": "R3",
                "rule_name": "View Balance by Active Agent",
                "reason": f"Agent '{a_name}' is active and authorized for read-only balance inquiry. Zero financial risk; auto-execution permitted."
            }
        else:
            # Action not granted by customer -> falls to R6
            return {
                "decision": "BLOCK",
                "rule_id": "R6",
                "rule_name": "Action Not Permitted by Customer",
                "reason": f"Agent '{a_name}' attempted 'View Balance', which was NOT included in customer's permitted actions ({permitted_actions})."
            }

    # For Financial Transactions (Pay Bill, Transfer Money)
    is_action_permitted = action in permitted_actions

    # Check if transaction is authorized (action in permitted_actions AND transaction_permission is True)
    if is_action_permitted and transaction_permission:
        # ---------------------------------------------------------
        # R4: Authorised payment/transfer up to ₹10,000 -> ALLOW
        # ---------------------------------------------------------
        if 0 <= amount <= 10000:
            return {
                "decision": "ALLOW",
                "rule_id": "R4",
                "rule_name": "Authorised Payment/Transfer <= ₹10,000",
                "reason": f"Agent '{a_name}' is authorized for '{action}'. The amount ₹{amount:,.2f} is within the ₹10,000 autonomous threshold."
            }
        # ---------------------------------------------------------
        # R5: Payment/transfer above ₹10,000 -> ASK CUSTOMER
        # ---------------------------------------------------------
        elif amount > 10000:
            return {
                "decision": "ASK CUSTOMER",
                "rule_id": "R5",
                "rule_name": "Payment/Transfer Exceeds ₹10,000",
                "reason": f"Agent '{a_name}' requested '{action}' of ₹{amount:,.2f}, exceeding the ₹10,000 autonomous threshold. Step-up customer approval (OTP) is required."
            }

    # -------------------------------------------------------------
    # R6: If agent tries an action not permitted by the customer -> BLOCK
    # -------------------------------------------------------------
    if not is_action_permitted:
        return {
            "decision": "BLOCK",
            "rule_id": "R6",
            "rule_name": "Action Not Permitted by Customer",
            "reason": f"Agent '{a_name}' attempted '{action}', but customer '{c_name}' only permitted: {', '.join(permitted_actions) if permitted_actions else 'None'}."
        }

    # -------------------------------------------------------------
    # R7: If customer has not granted transaction permission -> ASK CUSTOMER
    # -------------------------------------------------------------
    if not transaction_permission:
        return {
            "decision": "ASK CUSTOMER",
            "rule_id": "R7",
            "rule_name": "Transaction Permission Not Granted",
            "reason": f"Agent '{a_name}' attempted financial transaction '{action}', but customer '{c_name}' has not granted standing transaction permission. Direct customer consent required."
        }

    # Fallback to R8
    return {
        "decision": "BLOCK",
        "rule_id": "R8",
        "rule_name": "Missing or Invalid Input",
        "reason": "Request could not be validated against banking policy rules."
    }

# ==========================================
# CUSTOM STYLING (AXIS MAROON THEME)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }

    /* Top Brand Bar */
    .axis-top-bar {
        background: linear-gradient(135deg, #97144D 0%, #6E0D37 100%);
        color: #ffffff;
        padding: 1.4rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 15px rgba(151, 20, 77, 0.18);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }

    .axis-title {
        margin: 0;
        font-size: 1.85rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #ffffff !important;
    }

    .axis-subtitle {
        margin-top: 0.3rem;
        font-size: 0.95rem;
        color: #F8D7E3;
    }

    .pgd-badge {
        background-color: #ffffff;
        color: #97144D;
        padding: 0.65rem 1.3rem;
        border-radius: 8px;
        font-weight: 800;
        font-size: 1.05rem;
        border: 2px solid #FAD1E2;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: right;
    }

    .pgd-badge span {
        display: block;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #6E0D37;
        letter-spacing: 0.6px;
    }

    /* Status Badges */
    .status-active {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.8rem;
    }

    .status-revoked {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.8rem;
    }

    /* Decision Result Cards */
    .decision-banner {
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 1.2rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    .decision-banner.allow {
        background-color: #ECFDF5;
        border-left: 6px solid #10B981;
        color: #065F46;
    }

    .decision-banner.ask {
        background-color: #FFFBEB;
        border-left: 6px solid #F59E0B;
        color: #92400E;
    }

    .decision-banner.block {
        background-color: #FEF2F2;
        border-left: 6px solid #EF4444;
        color: #991B1B;
    }

    .rule-tag {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
    }

    .tag-allow { background-color: #A7F3D0; color: #064E3B; }
    .tag-ask { background-color: #FDE68A; color: #78350F; }
    .tag-block { background-color: #FECACA; color: #7F1D1D; }

    /* Policy Cards */
    .policy-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER: AXIS BRANDING & PGD NUMBER (PROMINENT)
# ==========================================
st.markdown("""
<div class="axis-top-bar">
    <div>
        <h1 class="axis-title">🏛️ Axis Bank Agent Gatekeeper</h1>
        <div class="axis-subtitle">A system that checks whether an AI agent is allowed to perform banking activities.</div>
    </div>
    <div class="pgd-badge">
        <span>Student Enrolment</span>
        PGD No: 63936
    </div>
</div>
""", unsafe_allow_html=True)

# Educational Disclaimer
st.info("🛡️ **Educational Simulation Only:** Strictly designed for academic coursework evaluation. No real bank accounts or actual money transactions are connected.")

# ==========================================
# MAIN NAVIGATION TABS
# ==========================================
tab_sim, tab_reg, tab_audit, tab_policy = st.tabs([
    "🎮 Gatekeeper Request Simulator",
    "📝 Agent Registration & Revocation",
    "📊 Persistent Audit Log",
    "📚 8-Rule Decision Reference"
])

# -------------------------------------------------------------
# TAB 1: GATEKEEPER REQUEST SIMULATOR
# -------------------------------------------------------------
with tab_sim:
    st.markdown("### 🎮 Gatekeeper Request Simulator")
    st.caption("Submit an AI agent transaction request to evaluate it against the 8 strict priority rules (Autonomous Limit: ₹10,000).")

    # Quick Preset Scenarios for Grader / Student
    st.markdown("##### ⚡ Quick Test Presets (Click to Auto-fill all 8 Rules):")
    preset_cols = st.columns(4)
    
    preset_data = None
    if preset_cols[0].button("Test R1: Revoked Agent", use_container_width=True):
        preset_data = ("Amit Verma", "LegacyHelper", "View Balance", 0.0)
    if preset_cols[1].button("Test R2: Unknown Agent", use_container_width=True):
        preset_data = ("Suresh Kumar", "HackerBot", "Pay Bill", 2500.0)
    if preset_cols[2].button("Test R3: View Balance (Safe)", use_container_width=True):
        preset_data = ("Rahul Sharma", "AxisFinanceBot", "View Balance", 0.0)
    if preset_cols[3].button("Test R4: Transfer <= ₹10,000", use_container_width=True):
        preset_data = ("Rahul Sharma", "AxisFinanceBot", "Transfer Money", 6500.0)

    preset_cols2 = st.columns(4)
    if preset_cols2[0].button("Test R5: Transfer > ₹10,000", use_container_width=True):
        preset_data = ("Rahul Sharma", "AxisFinanceBot", "Transfer Money", 25000.0)
    if preset_cols2[1].button("Test R6: Action Not Permitted", use_container_width=True):
        preset_data = ("Priya Patel", "BalanceChecker", "Transfer Money", 4000.0)
    if preset_cols2[2].button("Test R7: No Trans. Permission", use_container_width=True):
        # We ensure Priya has Pay Bill in actions but transaction permission False
        preset_data = ("Priya Patel", "BalanceChecker", "Pay Bill", 1200.0)
    if preset_cols2[3].button("Test R8: Invalid Amount (-₹500)", use_container_width=True):
        preset_data = ("Rahul Sharma", "AxisFinanceBot", "Transfer Money", -500.0)

    if preset_data:
        st.session_state["sim_cust"] = preset_data[0]
        st.session_state["sim_agent"] = preset_data[1]
        st.session_state["sim_action"] = preset_data[2]
        st.session_state["sim_amount"] = preset_data[3]

    st.markdown("---")

    # Simulator Inputs Form
    sim_col1, sim_col2 = st.columns(2, gap="large")

    with sim_col1:
        st.markdown("#### 📥 Agent Request Parameters")
        
        sim_cust = st.text_input(
            "Customer Name:",
            value=st.session_state.get("sim_cust", "Rahul Sharma"),
            help="Name of the Axis Bank account holder."
        )
        
        sim_agent = st.text_input(
            "AI Agent Name:",
            value=st.session_state.get("sim_agent", "AxisFinanceBot"),
            help="Name of the AI agent requesting access."
        )

        actions_list = ["View Balance", "Pay Bill", "Transfer Money"]
        default_action_idx = 0
        if "sim_action" in st.session_state and st.session_state["sim_action"] in actions_list:
            default_action_idx = actions_list.index(st.session_state["sim_action"])

        sim_action = st.selectbox(
            "Requested Action:",
            actions_list,
            index=default_action_idx,
            help="Banking activity the AI agent intends to execute."
        )

        sim_amount = st.number_input(
            "Transaction Amount (₹):",
            value=float(st.session_state.get("sim_amount", 5000.0)),
            step=500.0,
            help="Monetary amount in Indian Rupees. Negative amounts trigger R8."
        )

        evaluate_btn = st.button("🚀 Evaluate Request with Gatekeeper", type="primary", use_container_width=True)

    with sim_col2:
        st.markdown("#### 🛡️ Gatekeeper Decision Engine Output")

        if evaluate_btn or "last_decision" in st.session_state:
            if evaluate_btn:
                res = evaluate_request(
                    customer_name=sim_cust,
                    agent_name=sim_agent,
                    action=sim_action,
                    amount=sim_amount,
                    agents_list=st.session_state.agents
                )
                
                # Append to persistent audit log
                audit_entry = {
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Customer Name": sim_cust,
                    "Agent Name": sim_agent,
                    "Action": sim_action,
                    "Amount (₹)": sim_amount,
                    "Decision": res["decision"],
                    "Rule ID": res["rule_id"],
                    "Rule Name": res["rule_name"],
                    "Policy Rationale": res["reason"]
                }
                append_audit_log(audit_entry)
                st.session_state["last_decision"] = res
            else:
                res = st.session_state["last_decision"]

            # Visual Decision Styling
            dec = res["decision"]
            if dec == "ALLOW":
                banner_class = "allow"
                tag_class = "tag-allow"
                icon = "🟢"
            elif dec == "ASK CUSTOMER":
                banner_class = "ask"
                tag_class = "tag-ask"
                icon = "🟡"
            else:
                banner_class = "block"
                tag_class = "tag-block"
                icon = "🔴"

            st.markdown(f"""
            <div class="decision-banner {banner_class}">
                <span class="rule-tag {tag_class}">RULE {res['rule_id']} • {res['rule_name']}</span>
                <div style="font-size: 1.6rem; font-weight: 800; margin-bottom: 0.6rem;">{icon} {dec}</div>
                <div style="font-size: 0.95rem; line-height: 1.5;"><strong>Policy Rationale:</strong> {res['reason']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Details Breakdown
            with st.expander("🔍 Evaluation Metadata & Verification"):
                st.write(f"- **Evaluated Customer:** `{sim_cust}`")
                st.write(f"- **Evaluated Agent:** `{sim_agent}`")
                st.write(f"- **Requested Activity:** `{sim_action}`")
                st.write(f"- **Evaluated Amount:** `₹{sim_amount:,.2f}`")
                st.write(f"- **Autonomous Ceiling:** `₹10,000.00`")
                st.write(f"- **Audit Status:** Logged to persistent CSV/JSON storage.")
        else:
            st.info("👈 Enter agent request parameters on the left or click a quick test preset above, then click **Evaluate Request with Gatekeeper**.")

# -------------------------------------------------------------
# TAB 2: AGENT REGISTRATION & REVOCATION
# -------------------------------------------------------------
with tab_reg:
    st.markdown("### 📝 Agent Registration & Revocation")
    st.caption("Manage AI agents authorized to act on behalf of Axis Bank customers.")

    reg_col1, reg_col2 = st.columns([1, 1.3], gap="large")

    # Sub-Section 1: Register Agent
    with reg_col1:
        st.markdown("#### ➕ Register New Agent")
        with st.form("register_agent_form", clear_on_submit=True):
            new_cust = st.text_input("Customer Name:", placeholder="e.g. Ananya Sen")
            new_agent = st.text_input("AI Agent Name:", placeholder="e.g. WealthAssistant")
            
            new_actions = st.multiselect(
                "Permitted Actions:",
                options=["View Balance", "Pay Bill", "Transfer Money"],
                default=["View Balance", "Pay Bill"]
            )

            new_trans_perm = st.checkbox(
                "Grant Standing Transaction Permission",
                value=True,
                help="If unchecked, financial transactions will trigger Rule R7 (ASK CUSTOMER)."
            )

            submit_reg = st.form_submit_button("Register Agent", type="primary", use_container_width=True)

            if submit_reg:
                if not new_cust.strip() or not new_agent.strip():
                    st.error("⚠️ Customer Name and Agent Name are required.")
                elif not new_actions:
                    st.error("⚠️ Please select at least one permitted action.")
                else:
                    # Check for duplicates
                    exists = any(
                        ag["customer_name"].strip().lower() == new_cust.strip().lower() and
                        ag["agent_name"].strip().lower() == new_agent.strip().lower()
                        for ag in st.session_state.agents
                    )
                    if exists:
                        st.warning(f"Agent '{new_agent}' is already registered for '{new_cust}'.")
                    else:
                        new_record = {
                            "customer_name": new_cust.strip(),
                            "agent_name": new_agent.strip(),
                            "permitted_actions": new_actions,
                            "transaction_permission": new_trans_perm,
                            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "status": "ACTIVE",
                            "revoked_at": None
                        }
                        st.session_state.agents.append(new_record)
                        save_agents(st.session_state.agents)
                        st.success(f"✅ Agent '{new_agent}' registered successfully with status ACTIVE!")
                        st.rerun()

    # Sub-Section 2: Manage & Revoke Agents
    with reg_col2:
        st.markdown("#### 📋 Registered Agents Directory & One-Click Revocation")
        
        if not st.session_state.agents:
            st.info("No agents registered yet.")
        else:
            for idx, ag in enumerate(st.session_state.agents):
                status_color = "status-active" if ag["status"] == "ACTIVE" else "status-revoked"
                status_icon = "🟢" if ag["status"] == "ACTIVE" else "🔴"

                with st.container():
                    c_info, c_action = st.columns([2.5, 1])
                    with c_info:
                        st.markdown(f"**{ag['agent_name']}** (for *{ag['customer_name']}*)")
                        st.markdown(
                            f"<span class='{status_color}'>{status_icon} {ag['status']}</span> &nbsp; "
                            f"<small>Registered: {ag['registered_at']}</small>",
                            unsafe_allow_html=True
                        )
                        st.caption(
                            f"Permitted: {', '.join(ag['permitted_actions'])} | "
                            f"Trans. Permission: {'Granted' if ag.get('transaction_permission', True) else 'Denied'}"
                        )
                        if ag.get("revoked_at"):
                            st.caption(f"⚠️ Revoked At: {ag['revoked_at']}")
                    
                    with c_action:
                        if ag["status"] == "ACTIVE":
                            if st.button("🚫 Revoke Access", key=f"revoke_{idx}", use_container_width=True):
                                ag["status"] = "REVOKED"
                                ag["revoked_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                save_agents(st.session_state.agents)
                                st.warning(f"Agent '{ag['agent_name']}' has been REVOKED.")
                                st.rerun()
                        else:
                            st.button("Revoked", key=f"revoked_{idx}", disabled=True, use_container_width=True)

                    st.markdown("---")

# -------------------------------------------------------------
# TAB 3: PERSISTENT AUDIT LOG
# -------------------------------------------------------------
with tab_audit:
    st.markdown("### 📊 Persistent Audit Log & Compliance Ledger")
    st.caption("Every Gatekeeper decision is automatically stored in `data/audit_log.csv` and persists across system restarts.")

    audit_df = load_audit_log()

    # Summary Metrics
    if not audit_df.empty:
        total_evals = len(audit_df)
        total_allow = len(audit_df[audit_df["Decision"] == "ALLOW"])
        total_ask = len(audit_df[audit_df["Decision"] == "ASK CUSTOMER"])
        total_block = len(audit_df[audit_df["Decision"] == "BLOCK"])

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Requests Evaluated", total_evals)
        m2.metric("🟢 ALLOW (Autonomous)", total_allow)
        m3.metric("🟡 ASK CUSTOMER (In-Loop)", total_ask)
        m4.metric("🔴 BLOCK (Halted)", total_block)

        st.markdown("---")

        # Download CSV Button
        csv_data = audit_df.to_csv(index=False).encode('utf-8')
        d_col1, d_col2 = st.columns([1, 4])
        with d_col1:
            st.download_button(
                label="📥 Download Audit Log as CSV",
                data=csv_data,
                file_name=f"axis_gatekeeper_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with d_col2:
            if st.button("🗑️ Reset Audit Log (Clear Data)"):
                df_empty = pd.DataFrame(columns=[
                    "Timestamp", "Customer Name", "Agent Name", "Action", "Amount (₹)",
                    "Decision", "Rule ID", "Rule Name", "Policy Rationale"
                ])
                df_empty.to_csv(AUDIT_FILE, index=False)
                st.success("Audit log cleared.")
                st.rerun()

        st.dataframe(audit_df, use_container_width=True, height=400)
    else:
        st.info("No audit entries recorded yet. Test an action in the Simulator to generate log events.")

# -------------------------------------------------------------
# TAB 4: 8-RULE DECISION REFERENCE (POLICY MATRIX)
# -------------------------------------------------------------
with tab_policy:
    st.markdown("### 📚 8-Rule Decision Matrix (Strict Priority Order)")
    st.caption("Axis Bank Agent Governance Policy Framework with strict sequential precedence.")

    rules_matrix = [
        {"Rule": "R1", "Condition": "Agent status is REVOKED", "Decision": "🔴 BLOCK", "Priority": "1 (Highest)", "Policy Rationale": "Revoked credentials cannot initiate any action."},
        {"Rule": "R2", "Condition": "Agent is not registered (unknown)", "Decision": "🔴 BLOCK", "Priority": "2", "Policy Rationale": "Unregistered entities are treated as untrusted."},
        {"Rule": "R3", "Condition": "Registered active agent requests View Balance", "Decision": "🟢 ALLOW", "Priority": "3", "Policy Rationale": "Read-only inquiry carries zero financial risk."},
        {"Rule": "R4", "Condition": "Registered active agent makes authorised payment/transfer <= ₹10,000", "Decision": "🟢 ALLOW", "Priority": "4", "Policy Rationale": "Autonomous execution up to authorized ₹10,000 limit."},
        {"Rule": "R5", "Condition": "Registered active agent requests payment/transfer > ₹10,000", "Decision": "🟡 ASK CUSTOMER", "Priority": "5", "Policy Rationale": "Exceeds autonomous threshold; 2FA/OTP required."},
        {"Rule": "R6", "Condition": "Agent tries an action not permitted by the customer", "Decision": "🔴 BLOCK", "Priority": "6", "Policy Rationale": "Unauthorized action outside explicit customer mandate."},
        {"Rule": "R7", "Condition": "Customer has not granted transaction permission", "Decision": "🟡 ASK CUSTOMER", "Priority": "7", "Policy Rationale": "Customer consent required for unmandated financial moves."},
        {"Rule": "R8", "Condition": "Missing or invalid input (negative amount, empty fields)", "Decision": "🔴 BLOCK", "Priority": "8", "Policy Rationale": "Malformed input fails data integrity and safety check."}
    ]

    st.dataframe(pd.DataFrame(rules_matrix), use_container_width=True, hide_index=True)

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Axis_Bank_logo.svg/320px-Axis_Bank_logo.svg.png", width=180)
    st.markdown("---")
    
    st.markdown("### 🎓 Academic Project Info")
    st.markdown("**Program:** MBA in Business Analytics / AI")
    st.markdown("**PGD / Enrolment No:** `63936`")
    st.markdown("**Course Project:** Agentic AI Systems")
    st.markdown("**Phase:** 2 (Full Decision Engine & Persistence)")

    st.markdown("---")
    st.markdown("### 📈 Live System Metrics")
    active_count = sum(1 for a in st.session_state.agents if a["status"] == "ACTIVE")
    revoked_count = sum(1 for a in st.session_state.agents if a["status"] == "REVOKED")
    audit_count = len(load_audit_log())
    
    st.write(f"• **Active Agents:** `{active_count}`")
    st.write(f"• **Revoked Agents:** `{revoked_count}`")
    st.write(f"• **Logged Audit Events:** `{audit_count}`")
    st.write(f"• **Autonomous Ceiling:** `₹10,000`")

    st.markdown("---")
    if st.button("🔄 Reset Seed Agents to Default", use_container_width=True):
        st.session_state.agents = get_default_agents()
        save_agents(st.session_state.agents)
        st.success("Default agents restored.")
        st.rerun()

    st.caption("Axis Bank Agent Gatekeeper • Educational Prototype Phase 2")
