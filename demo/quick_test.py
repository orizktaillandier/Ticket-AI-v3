"""
Quick test to verify classifier reliability
"""
import sys
from classifier import TicketClassifier
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# Test with a simple ticket
test_ticket = """
Subject: Syndicator_Export_1 export issues - Dealership_3

Hi team,

We need to cancel the Syndicator_Export_1 export for Dealership_3. The client has requested this to be done ASAP.

Thanks,
Support Agent_1
Dealer Support Specialist
"""

print("Testing classifier reliability...")
print("=" * 80)

classifier = TicketClassifier()
result = classifier.classify(test_ticket, "Syndicator_Export_1 export issues - Dealership_3")

print("\n✅ SUCCESS" if result["success"] else "\n❌ FAILED")

if result["success"]:
    print("\n📊 CLASSIFICATION:")
    for key, value in result["classification"].items():
        print(f"  {key}: {value}")

    print("\n🤖 ENTITIES:")
    for key, value in result["entities"].items():
        print(f"  {key}: {value}")

    print("\n✉️ SUGGESTED RESPONSE:")
    print(result.get("suggested_response", "No response generated"))
else:
    print(f"\nError: {result.get('error')}")

print("\n" + "=" * 80)
