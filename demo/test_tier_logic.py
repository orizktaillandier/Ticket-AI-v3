"""
Test tier escalation logic with various ticket scenarios
"""
import sys
from classifier import TicketClassifier
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# Test scenarios
test_tickets = [
    {
        "name": "Simple Product Activation",
        "text": "Please setup Syndicator_Export_5 for Dealership_1.",
        "expected_tier": "Tier 1"
    },
    {
        "name": "Product Activation with Question",
        "text": "Please setup Syndicator_Export_5 for Dealership_1. When will this be live?",
        "expected_tier": "Tier 2"
    },
    {
        "name": "Product Activation with Multiple Questions",
        "text": "Hi, can you activate the feed for Dealership_2? Also, do we need an order? And what's the timeline?",
        "expected_tier": "Tier 2"
    },
    {
        "name": "Product Activation with Special Request",
        "text": "Please setup the feed for Dealership_3. We need this rushed by tomorrow.",
        "expected_tier": "Tier 2"
    },
    {
        "name": "Product Activation - Very Simple",
        "text": "Activate Syndicator_Export_1 for Dealership_5. Thanks.",
        "expected_tier": "Tier 1"
    },
    {
        "name": "Product Activation with Concern",
        "text": "Setup the feed. The client mentioned they had issues before, so please be careful.",
        "expected_tier": "Tier 2"
    },
    {
        "name": "Problem/Bug (should always be Tier 2+)",
        "text": "The feed is not working for Dealership_1.",
        "expected_tier": "Tier 2"
    }
]

print("=" * 80)
print("TESTING TIER ESCALATION LOGIC")
print("=" * 80)

classifier = TicketClassifier()

passed = 0
failed = 0

for test in test_tickets:
    print(f"\n{'=' * 80}")
    print(f"TEST: {test['name']}")
    print(f"{'=' * 80}")
    print(f"Ticket: {test['text']}")
    print(f"Expected: {test['expected_tier']}")

    result = classifier.classify(test['text'], "")

    if result["success"]:
        tier = result["classification"]["tier"]
        category = result["classification"]["category"]
        entities = result["entities"]

        print(f"Classified: {tier}")
        print(f"Category: {category}")

        # Show why it was classified that way
        questions = entities.get("additional_questions", [])
        special = entities.get("special_requests", [])

        if questions:
            print(f"Questions detected: {questions}")
        if special:
            print(f"Special requests detected: {special}")

        if tier == test["expected_tier"]:
            print("✅ PASSED")
            passed += 1
        else:
            print(f"❌ FAILED - Expected {test['expected_tier']} but got {tier}")
            failed += 1
    else:
        print(f"❌ Classification failed: {result.get('error')}")
        failed += 1

print(f"\n{'=' * 80}")
print(f"RESULTS: {passed} passed, {failed} failed")
print(f"{'=' * 80}")
