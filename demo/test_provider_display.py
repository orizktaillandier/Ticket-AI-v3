"""
Test provider field display
"""
import sys
from classifier import TicketClassifier
from dotenv import load_dotenv
import json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

test_tickets = [
    {
        "name": "Import Ticket 1",
        "text": "Hi, please setup Provider_Import_1 for Dealership_4. Thanks."
    },
    {
        "name": "Import Ticket 2",
        "text": "The Provider_Import_2 feed for Dealership_5 is not working correctly."
    },
    {
        "name": "Export Ticket",
        "text": "Please activate Syndicator_Export_3 for Dealership_2."
    }
]

classifier = TicketClassifier()

print("=" * 80)
print("TESTING PROVIDER FIELD DISPLAY")
print("=" * 80)

for test in test_tickets:
    print(f"\n{'=' * 80}")
    print(f"TEST: {test['name']}")
    print(f"Text: {test['text']}")
    print(f"{'=' * 80}")

    result = classifier.classify(test['text'], "")

    if result["success"]:
        classification = result["classification"]

        print(f"\n📊 CLASSIFICATION JSON:")
        print(json.dumps(classification, indent=2))

        print(f"\n✅ Provider field: '{classification.get('provider', 'MISSING')}'")
        print(f"✅ Syndicator field: '{classification.get('syndicator', 'MISSING')}'")
        print(f"✅ Sub-category: {classification['sub_category']}")

        # Verify correct assignment
        if classification['sub_category'] == "Import":
            if classification['provider']:
                print(f"✅ CORRECT: Import ticket has provider assigned")
            else:
                print(f"❌ ERROR: Import ticket missing provider!")

        if classification['sub_category'] == "Export":
            if classification['syndicator']:
                print(f"✅ CORRECT: Export ticket has syndicator assigned")
            else:
                print(f"❌ ERROR: Export ticket missing syndicator!")

print(f"\n{'=' * 80}")
