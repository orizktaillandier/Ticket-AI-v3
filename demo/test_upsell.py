"""Test upsell intelligence"""
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
from upsell_intelligence import UpsellIntelligence
from client_health import ClientHealthEngine
import json

ui = UpsellIntelligence()
he = ClientHealthEngine()

with open('data/dealer_revenue.json') as f:
    revenue = json.load(f)

all_histories = he._generate_mock_history()
histories = {did: all_histories.get(did, []) for did in revenue.keys()}
summary = ui.get_portfolio_upsell_summary(revenue, histories)

print(f'Total Opportunities: {summary["total_opportunities"]}')
print(f'Total Potential Revenue: ${summary["total_potential_revenue"]:,.0f}')
print(f'High Priority: {len(summary["high_priority"])}')
print(f'\nTop 3 Opportunities:')
for opp in summary["opportunities"][:3]:
    rev_increase = opp.get("revenue_increase", 0)
    rec_package = opp.get("recommended_package", "N/A")
    print(f'  - {opp["dealer_name"]}: {opp["current_package"]} → {rec_package} (+${rev_increase:,.0f}/year)')
    print(f'    Signals: {[s["keyword"] for s in opp.get("signals_detected", [])]}')
