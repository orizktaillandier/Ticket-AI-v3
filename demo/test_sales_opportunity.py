"""Test sales opportunity detection"""
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from sales_intelligence import SalesIntelligence

si = SalesIntelligence()

# Test ticket: Multi-location expansion
test1 = si.detect_opportunity(
    ticket_text="Hi, we're opening a second location next month. Do you offer multi-location support?",
    ticket_subject="Multi-location setup",
    dealer_id="1001",
    dealer_name="Dealership_1",
    current_package="Standard"
)

print("Test 1: Multi-location expansion")
print(f"Has Opportunity: {test1['has_opportunity']}")
print(f"Type: {test1['opportunity_type']}")
print(f"Revenue: ${test1['potential_revenue']:,}")
print(f"Priority: {test1['priority']}")
print(f"Signals: {[s['keyword'] for s in test1['signals']]}")
print()

# Test ticket: Advanced features request
test2 = si.detect_opportunity(
    ticket_text="Is there a way to get API access and custom integration with our CRM?",
    ticket_subject="API access inquiry",
    dealer_id="1005",
    dealer_name="Dealership_5",
    current_package="Basic"
)

print("Test 2: Advanced features (Basic → Premium)")
print(f"Has Opportunity: {test2['has_opportunity']}")
print(f"Type: {test2['opportunity_type']}")
print(f"Revenue: ${test2['potential_revenue']:,}")
print(f"Priority: {test2['priority']}")
print(f"Talking Points: {test2['talking_points'][0] if test2['talking_points'] else 'None'}")
