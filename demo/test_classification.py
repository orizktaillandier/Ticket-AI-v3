"""
Test script to verify classification works correctly for all sample tickets
"""
import json
import os
import sys
from classifier import TicketClassifier
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

def test_all_tickets():
    """Test classification on all sample tickets"""

    # Initialize classifier
    classifier = TicketClassifier()

    # Load sample tickets
    with open("mock_data/sample_tickets.json", "r", encoding="utf-8") as f:
        tickets = json.load(f)

    print("=" * 80)
    print("TESTING ALL SAMPLE TICKETS")
    print("=" * 80)

    # Track results
    all_passed = True
    results = []

    for ticket in tickets:
        ticket_id = ticket["ticket_number"]
        print(f"\n{'=' * 80}")
        print(f"TICKET {ticket_id}: {ticket['subject']}")
        print(f"{'=' * 80}")

        # Build full ticket text
        ticket_text = f"Subject: {ticket['subject']}\n\n{ticket['description']}"
        if ticket.get('threads'):
            ticket_text += "\n\nThread Updates:\n"
            for thread in ticket['threads']:
                ticket_text += f"- {thread['author_name']}: {thread['content']}\n"

        # Classify
        result = classifier.classify(ticket_text, ticket["subject"])

        # Extract the actual classification from the result
        if not result.get("success"):
            print(f"\n❌ CLASSIFICATION FAILED")
            results.append({
                "ticket_id": ticket_id,
                "status": "FAILED",
                "missing_fields": ["Classification API failed"]
            })
            all_passed = False
            continue

        classification = result.get("classification", {})

        # Check all fields (using correct field names)
        required_fields = [
            "contact", "dealer_name", "dealer_id", "rep",
            "category", "sub_category", "inventory_type", "tier"
        ]

        # Either syndicator OR provider must be filled
        syndicator_or_provider = bool(classification.get("syndicator")) or bool(classification.get("provider"))

        # Verify all required fields are filled
        missing_fields = []
        for field in required_fields:
            if not classification.get(field):
                missing_fields.append(field)

        # Check syndicator/provider
        if not syndicator_or_provider:
            missing_fields.append("syndicator OR provider")

        # Display results
        print("\nCLASSIFICATION RESULTS:")
        print("-" * 80)
        for key, value in classification.items():
            marker = "✓" if value else "✗"
            print(f"{marker} {key}: {value}")

        # Status
        if missing_fields:
            print(f"\n❌ FAILED - Missing fields: {', '.join(missing_fields)}")
            all_passed = False
            results.append({
                "ticket_id": ticket_id,
                "status": "FAILED",
                "missing_fields": missing_fields
            })
        else:
            print("\n✅ PASSED - All fields populated correctly")
            results.append({
                "ticket_id": ticket_id,
                "status": "PASSED"
            })

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    passed_count = sum(1 for r in results if r["status"] == "PASSED")
    failed_count = sum(1 for r in results if r["status"] == "FAILED")

    print(f"\nTotal Tickets: {len(results)}")
    print(f"✅ Passed: {passed_count}")
    print(f"❌ Failed: {failed_count}")

    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Classification is working correctly.")
    else:
        print("\n⚠️ SOME TESTS FAILED. Review the results above.")
        print("\nFailed tickets:")
        for r in results:
            if r["status"] == "FAILED":
                print(f"  - {r['ticket_id']}: Missing {', '.join(r['missing_fields'])}")

    print("=" * 80)

    return all_passed

if __name__ == "__main__":
    test_all_tickets()
