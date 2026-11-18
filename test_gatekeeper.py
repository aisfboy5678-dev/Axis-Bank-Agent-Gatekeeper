import os
import sys
from app import evaluate_request, get_default_agents

def run_tests():
    agents = get_default_agents()
    print("=" * 60)
    print("AXIS BANK AGENT GATEKEEPER: VERIFYING 6 COMPULSORY TEST CASES")
    print("=" * 60)

    # -------------------------------------------------------------
    # 6 COMPULSORY ASSIGNMENT TEST CASES
    # -------------------------------------------------------------
    
    # Test 1: Known registered agent viewing balance -> ALLOW (R3)
    t1 = evaluate_request("Rahul Sharma", "AxisFinanceBot", "View Balance", 0, agents)
    assert t1["rule_id"] == "R3" and t1["decision"] == "ALLOW", f"Test 1 Failed: {t1}"
    print("✅ Test 1 Passed: Known registered agent viewing balance -> ALLOW (Rule R3)")

    # Test 2: Unknown unregistered agent transferring ₹2,000 -> BLOCK (R2)
    t2 = evaluate_request("Rahul Sharma", "ShadowBot", "Transfer Money", 2000, agents)
    assert t2["rule_id"] == "R2" and t2["decision"] == "BLOCK", f"Test 2 Failed: {t2}"
    print("✅ Test 2 Passed: Unknown unregistered agent transferring ₹2,000 -> BLOCK (Rule R2)")

    # Test 3: Registered agent paying ₹15,000 (above ₹10,000 limit) -> ASK CUSTOMER (R5)
    t3 = evaluate_request("Rahul Sharma", "AxisFinanceBot", "Pay Bill", 15000, agents)
    assert t3["rule_id"] == "R5" and t3["decision"] == "ASK CUSTOMER", f"Test 3 Failed: {t3}"
    print("✅ Test 3 Passed: Registered agent paying ₹15,000 (above limit) -> ASK CUSTOMER (Rule R5)")

    # Test 4: Registered agent paying ₹5,000 (within ₹10,000 limit) -> ALLOW (R4)
    t4 = evaluate_request("Rahul Sharma", "AxisFinanceBot", "Pay Bill", 5000, agents)
    assert t4["rule_id"] == "R4" and t4["decision"] == "ALLOW", f"Test 4 Failed: {t4}"
    print("✅ Test 4 Passed: Registered agent paying ₹5,000 (within limit) -> ALLOW (Rule R4)")

    # Test 5: Revoked agent trying to pay ₹500 -> BLOCK (R1)
    t5 = evaluate_request("Amit Verma", "LegacyHelper", "Pay Bill", 500, agents)
    assert t5["rule_id"] == "R1" and t5["decision"] == "BLOCK", f"Test 5 Failed: {t5}"
    print("✅ Test 5 Passed: Revoked agent trying to pay ₹500 -> BLOCK (Rule R1)")

    # Test 6: Registered agent trying an unauthorised transfer action -> BLOCK (R6)
    t6 = evaluate_request("Priya Patel", "BalanceChecker", "Transfer Money", 3000, agents)
    assert t6["rule_id"] == "R6" and t6["decision"] == "BLOCK", f"Test 6 Failed: {t6}"
    print("✅ Test 6 Passed: Registered agent trying an unauthorised transfer action -> BLOCK (Rule R6)")

    print("\n" + "=" * 60)
    print("ADDITIONAL EDGE CASES (R7 & R8):")
    print("=" * 60)

    # Edge Case R7: Customer has not granted transaction permission -> ASK CUSTOMER (R7)
    agents_copy = [dict(a) for a in agents]
    for a in agents_copy:
        if a["agent_name"] == "BalanceChecker":
            a["permitted_actions"] = ["View Balance", "Pay Bill"]
            a["transaction_permission"] = False
    t7 = evaluate_request("Priya Patel", "BalanceChecker", "Pay Bill", 1500, agents_copy)
    assert t7["rule_id"] == "R7" and t7["decision"] == "ASK CUSTOMER", f"Test R7 Failed: {t7}"
    print("✅ Edge Case Passed: No transaction permission -> ASK CUSTOMER (Rule R7)")

    # Edge Case R8: Negative amount -> BLOCK (R8)
    t8_neg = evaluate_request("Rahul Sharma", "AxisFinanceBot", "Transfer Money", -500, agents)
    assert t8_neg["rule_id"] == "R8" and t8_neg["decision"] == "BLOCK", f"Test R8 Negative Failed: {t8_neg}"
    print("✅ Edge Case Passed: Negative amount (-₹500) -> BLOCK (Rule R8)")

    # Edge Case R8: Empty fields -> BLOCK (R8)
    t8_empty = evaluate_request("", "", "Transfer Money", 500, agents)
    assert t8_empty["rule_id"] == "R8" and t8_empty["decision"] == "BLOCK", f"Test R8 Empty Failed: {t8_empty}"
    print("✅ Edge Case Passed: Empty fields -> BLOCK (Rule R8)")

    print("\n🎉 ALL 6 COMPULSORY TEST CASES + 8 ENGINE RULES VERIFIED WITH 100% SUCCESS!")

if __name__ == "__main__":
    run_tests()
