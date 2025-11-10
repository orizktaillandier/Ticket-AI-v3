"""
Comprehensive test of all 11 sample tickets
"""
import sys
import json
from classifier import TicketClassifier
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# Load all sample tickets
with open("mock_data/sample_tickets.json", "r", encoding="utf-8") as f:
    tickets = json.load(f)

print("=" * 100)
print("TESTING ALL 11 SAMPLE TICKETS")
print("=" * 100)

classifier = TicketClassifier()

issues = []

for i, ticket in enumerate(tickets, 1):
    print(f"\n{'=' * 100}")
    print(f"TICKET {i}/11: {ticket['ticket_number']} - {ticket['subject']}")
    print(f"{'=' * 100}")

    full_text = f"Subject: {ticket['subject']}\n\n{ticket['description']}"
    if ticket.get('threads'):
        for thread in ticket['threads']:
            full_text += f"\n\n{thread['author_name']}: {thread['content']}"

    print(f"Text preview: {ticket['description'][:150]}...")

    result = classifier.classify(ticket['description'], ticket['subject'])

    if result["success"]:
        classification = result["classification"]
        entities = result["entities"]

        print(f"\n📊 CLASSIFICATION:")
        print(f"  Category: {classification['category']}")
        print(f"  Sub-category: {classification['sub_category']}")
        print(f"  Tier: {classification['tier']}")
        print(f"  Dealer: {classification['dealer_name']} (ID: {classification.get('dealer_id', 'N/A')})")
        print(f"  Rep: {classification['rep']}")
        if classification['syndicator']:
            print(f"  Syndicator: {classification['syndicator']}")
        if classification['provider']:
            print(f"  Provider: {classification['provider']}")
        print(f"  Inventory Type: {classification['inventory_type']}")
        print(f"  Sentiment: {entities.get('sentiment', 'N/A')}")

        # Check for potential issues
        issue_found = False

        # Issue 1: Missing dealer
        if not classification['dealer_name'] or classification['dealer_name'] == "Unknown Dealer":
            print(f"\n⚠️  WARNING: Dealer name not extracted")
            issues.append(f"Ticket {ticket['ticket_number']}: Missing dealer name")
            issue_found = True

        # Issue 2: Wrong category for obvious patterns
        desc_lower = ticket['description'].lower()
        if 'cancel' in desc_lower or 'désactiv' in desc_lower:
            if classification['category'] != "Product Cancellation":
                print(f"\n❌ ERROR: Should be 'Product Cancellation' but got '{classification['category']}'")
                issues.append(f"Ticket {ticket['ticket_number']}: Wrong category (expected Cancellation)")
                issue_found = True

        if 'not working' in desc_lower or 'issue' in desc_lower or 'problem' in desc_lower:
            if classification['category'] != "Problem / Bug":
                print(f"\n❌ ERROR: Should be 'Problem / Bug' but got '{classification['category']}'")
                issues.append(f"Ticket {ticket['ticket_number']}: Wrong category (expected Problem/Bug)")
                issue_found = True

        if 'activate' in desc_lower or 'setup' in desc_lower or 'activer' in desc_lower:
            if 'Product Activation' not in classification['category']:
                print(f"\n❌ ERROR: Should be 'Product Activation' but got '{classification['category']}'")
                issues.append(f"Ticket {ticket['ticket_number']}: Wrong category (expected Activation)")
                issue_found = True

        # Issue 3: Tier logic checks
        if classification['category'] == "Problem / Bug" and classification['tier'] not in ["Tier 2", "Tier 3"]:
            print(f"\n❌ ERROR: Problems should be Tier 2+, but got {classification['tier']}")
            issues.append(f"Ticket {ticket['ticket_number']}: Wrong tier for Problem")
            issue_found = True

        # Issue 4: Urgency detection
        if 'urgent' in desc_lower or 'asap' in desc_lower or 'critical' in desc_lower:
            if classification['tier'] != "Tier 3":
                print(f"\n⚠️  WARNING: Urgent ticket should be Tier 3, but got {classification['tier']}")
                issues.append(f"Ticket {ticket['ticket_number']}: Urgent but not Tier 3")
                issue_found = True

        if not issue_found:
            print(f"\n✅ Classification looks good!")

    else:
        print(f"\n❌ CLASSIFICATION FAILED: {result.get('error')}")
        issues.append(f"Ticket {ticket['ticket_number']}: Classification failed - {result.get('error')}")

print(f"\n\n{'=' * 100}")
print(f"SUMMARY")
print(f"{'=' * 100}")
print(f"Total tickets tested: {len(tickets)}")
print(f"Issues found: {len(issues)}")

if issues:
    print(f"\n❌ ISSUES DETECTED:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print(f"\n✅ ALL TICKETS CLASSIFIED CORRECTLY!")

print(f"{'=' * 100}")
