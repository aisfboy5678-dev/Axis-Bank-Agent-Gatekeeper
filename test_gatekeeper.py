import os
import sys
from app import evaluate_request, get_default_agents

def run_tests():
    agents = get_default_agents()
    print("Testing 8 Decision Rules...\n")

    # Test R1: Revoked Agent
    res_r1 = evaluate_request("Amit Verma", "LegacyHelper", "View Balance", 0, agents)
    assert res_r1["rule_id"] == "R1" and res_r1["decision"] == "BLOCK", f"R1 Failed: {res_r1}"
    print("✅ R1 (Revoked Agent -> BLOCK) Passed.")

    # Test R2: Unknown Agent
    res_r2 = evaluate_request("Suresh Kumar", "UnknownBot", "Pay Bill", 1000, agents)
    assert res_r2["rule_id"] == "R2" and res_r2["decision"] == "BLOCK", f"R2 Failed: {res_r2}"
    print("✅ R2 (Unknown Agent -> BLOCK) Passed.")

    # Test R3: View Balance by active agent
    res_r3 = evaluate_request("Rahul Sharma", "AxisFinanceBot", "View Balance", 0, agents)
    assert res_r3["rule_id"] == "R3" and res_r3["decision"] == "ALLOW", f"R3 Failed: {res_r3}"
    print("✅ R3 (View Balance -> ALLOW) Passed.")

    # Test R4: Authorised payment <= 10,000
    res_r4 = evaluate_request("Rahul Sharma", "AxisFinanceBot", "Transfer Money", 6500, agents)
    assert res_r4["rule_id"] == "R4" and res_r4["decision"] == "ALLOW", f"R4 Failed: {res_r4}"
    print("✅ R4 (Authorised payment <= ₹10,000 -> ALLOW) Passed.")

    # Test R5: Authorised payment > 10,000
    res_r5 = evaluate_request("Rahul Sharma", "AxisFinanceBot", "Transfer Money", 25000, agents)
    assert res_r5["rule_id"] == "R5" and res_r5["decision"] == "ASK CUSTOMER", f"R5 Failed: {res_r5}"
    print("✅ R5 (Payment > ₹10,000 -> ASK CUSTOMER) Passed.")

    # Test R6: Action not permitted by customer
    res_r6 = evaluate_request("Priya Patel", "BalanceChecker", "Transfer Money", 3000, agents)
    assert res_r6["rule_id"] == "R6" and res_r6["decision"] == "BLOCK", f"R6 Failed: {res_r6}"
    print("✅ R6 (Action not permitted -> BLOCK) Passed.")

    # Test R7: Customer has not granted transaction permission
    # Let's add Pay Bill to permitted actions for Priya Patel, but keep transaction_permission=False
    agents_copy = [dict(a) for a in agents]
    for a in agents_copy:
        if a["agent_name"] == "BalanceChecker":
            a["permitted_actions"] = ["View Balance", "Pay Bill"]
            a["transaction_permission"] = False
    res_r7 = evaluate_request("Priya Patel", "BalanceChecker", "Pay Bill", 1500, agents_copy)
    assert res_r7["rule_id"] == "R7" and res_r7["decision"] == "ASK CUSTOMER", f"R7 Failed: {res_r7}"
    print("✅ R7 (No transaction permission -> ASK CUSTOMER) Passed.")

    # Test R8: Negative amount
    res_r8_neg = evaluate_request("Rahul Sharma", "AxisFinanceBot", "Transfer Money", -500, agents)
    assert res_r8_neg["rule_id"] == "R8" and res_r8_neg["decision"] == "BLOCK", f"R8 Negative Failed: {res_r8_neg}"
    print("✅ R8 (Negative amount -> BLOCK) Passed.")

    # Test R8: Empty fields
    res_r8_empty = evaluate_request("", "", "Transfer Money", 500, agents)
    assert res_r8_empty["rule_id"] == "R8" and res_r8_empty["decision"] == "BLOCK", f"R8 Empty Failed: {res_r8_empty}"
    print("✅ R8 (Empty fields -> BLOCK) Passed.")

    print("\n🎉 ALL 8 DECISION RULES PASSED WITH 100% ACCURACY!")

if __name__ == "__main__":
    run_tests()
