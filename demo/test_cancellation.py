"""
Test Product Cancellation automation workflow
"""
import sys
from classifier import TicketClassifier
from automation_engine import AutomationEngine
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# Test ticket - Product Cancellation from 3rd party
test_ticket = {
    "ticket_id": "12355",
    "subject": "Cancel Syndicator_Export_3 feed - Dealership_2",
    "description": "Hi D2CMedia,\n\nPlease cancel the Syndicator_Export_3 feed for Dealership_2. The client has decided not to continue with this service.\n\nThanks,\nMike from Syndicator_Export_3",
    "requester_email": "mike@syndicator_export_3.com"
}

print("=" * 80)
print("TESTING PRODUCT CANCELLATION AUTOMATION")
print("=" * 80)

# Step 1: Classify the ticket
print("\n[STEP 1] Classifying ticket...")
classifier = TicketClassifier()
result = classifier.classify(test_ticket["description"], "")

if not result["success"]:
    print(f"❌ Classification failed: {result.get('error')}")
    sys.exit(1)

classification = result["classification"]
entities = result["entities"]

print(f"✓ Classification successful")
print(f"  Category: {classification['category']}")
print(f"  Tier: {classification['tier']}")
print(f"  Dealer: {classification['dealer_name']} (ID: {classification.get('dealer_id', 'N/A')})")
print(f"  Syndicator: {classification['syndicator']}")
print(f"  Rep: {classification['rep']}")

# Step 2: Check if automatable
print("\n[STEP 2] Checking automation eligibility...")
automation_engine = AutomationEngine()
can_automate, reason = automation_engine.can_automate(classification, entities)

print(f"  Can automate: {can_automate}")
print(f"  Reason: {reason}")

if not can_automate:
    print("\n❌ Ticket cannot be automated")
    sys.exit(0)

# Step 3: Execute automation
print("\n[STEP 3] Executing automated cancellation workflow...")
print("=" * 80)

automation_result = automation_engine.execute_automation(classification, entities, test_ticket)

if automation_result["success"]:
    print("\n" + "=" * 80)
    print("✅ AUTOMATION SUCCESSFUL")
    print("=" * 80)
    print(f"Execution time: {automation_result['execution_time']}s")
    print(f"Emails sent: {len(automation_result['emails_sent'])}")
    print(f"Internal comments: {len(automation_result['internal_comments'])}")

    print("\n[EMAILS SENT]")
    for email in automation_result['emails_sent']:
        print(f"\n  {email['timestamp']} - {email['type'].upper()}")
        print(f"  To: {email['to']}")
        print(f"  Subject: {email['subject']}")

    print("\n[FEED CANCELLED]")
    feed_info = automation_result['feed_cancelled']
    print(f"  Feed ID: {feed_info['feed_id']}")
    print(f"  Dealer: {feed_info['dealer_name']}")
    print(f"  Feed: {feed_info['feed_name']}")
    print(f"  Status: {feed_info['status']}")

else:
    print("\n❌ AUTOMATION FAILED")
    print(f"Error: {automation_result.get('error')}")

print("\n" + "=" * 80)
