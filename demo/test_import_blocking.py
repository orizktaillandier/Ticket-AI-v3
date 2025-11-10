"""
Test that ALL import tickets are classified as Tier 2+ (no Tier 1 automation)
"""
import sys
from classifier import TicketClassifier
from automation_engine import AutomationEngine
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# Test tickets - various import scenarios
test_tickets = [
    {
        "name": "Simple Import Setup Request",
        "description": "Please setup Provider_Import_1 for Dealership_5. Thanks.",
        "expected_tier": "Tier 2"
    },
    {
        "name": "Import Problem",
        "description": "The Provider_Import_2 feed for Dealership_4 is not working.",
        "expected_tier": "Tier 2"
    },
    {
        "name": "Import Activation Request",
        "description": "Hi, can you activate the import from Provider_Import_3 for Dealership_6?",
        "expected_tier": "Tier 2"
    }
]

print("=" * 80)
print("TESTING IMPORT BLOCKING (ALL IMPORTS SHOULD BE TIER 2+)")
print("=" * 80)

classifier = TicketClassifier()
automation_engine = AutomationEngine()

passed = 0
failed = 0

for test in test_tickets:
    print(f"\n{'=' * 80}")
    print(f"TEST: {test['name']}")
    print(f"{'=' * 80}")
    print(f"Ticket: {test['description']}")

    result = classifier.classify(test['description'], "")

    if result["success"]:
        classification = result["classification"]
        tier = classification["tier"]
        category = classification["category"]
        sub_category = classification["sub_category"]

        print(f"Category: {category}")
        print(f"Sub-category: {sub_category}")
        print(f"Tier: {tier}")

        # Check automation eligibility
        can_automate, reason = automation_engine.can_automate(classification, result.get("entities", {}))
        print(f"Can automate: {can_automate}")
        print(f"Reason: {reason}")

        # Verify tier is 2 or 3 (not 1)
        if tier != "Tier 1":
            print(f"✅ PASSED - Import correctly blocked from Tier 1 (classified as {tier})")
            passed += 1
        else:
            print(f"❌ FAILED - Import was classified as Tier 1 (should be Tier 2+)")
            failed += 1
    else:
        print(f"❌ Classification failed: {result.get('error')}")
        failed += 1

print(f"\n{'=' * 80}")
print(f"RESULTS: {passed}/{len(test_tickets)} passed")
print(f"{'=' * 80}")

if failed == 0:
    print("✅ ALL TESTS PASSED - Import blocking is working correctly!")
else:
    print(f"❌ {failed} tests failed - Import blocking needs adjustment")
