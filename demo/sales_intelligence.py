"""
Sales Opportunity Intelligence
Detects revenue opportunities from ticket content and customer conversations
"""

import json
from typing import Dict, List, Any
from datetime import datetime


class SalesIntelligence:
    """
    Analyzes ticket content to identify sales opportunities.
    """

    def __init__(self):
        """Initialize the sales intelligence engine."""

        # Feature request signals
        self.feature_signals = {
            "advanced_features": [
                "advanced reporting", "custom reports", "analytics dashboard",
                "api access", "webhook", "integration", "custom integration",
                "white label", "branded", "custom branding"
            ],
            "multi_location": [
                "multi-location", "multiple locations", "second location", "third location",
                "additional location", "new location", "another location", "expansion",
                "open new", "chain", "franchise", "all locations"
            ],
            "team_expansion": [
                "add user", "additional user", "more users", "team member",
                "new employee", "hire", "growing team", "expand team"
            ],
            "inventory_expansion": [
                "more inventory", "additional inventory", "increase capacity",
                "more vehicles", "expand inventory", "larger inventory"
            ],
            "premium_support": [
                "dedicated support", "priority support", "phone support",
                "faster response", "account manager", "dedicated rep"
            ],
            "new_product": [
                "what about", "do you offer", "can we get", "is there a way to",
                "how do we", "interested in", "looking for", "need to"
            ]
        }

        # Expansion indicators
        self.expansion_signals = {
            "growth": [
                "growing", "expansion", "scale", "scaling up", "expanding",
                "increase", "more customers", "higher volume"
            ],
            "new_market": [
                "new market", "new territory", "another state", "different region",
                "opening in", "launching in"
            ],
            "acquisition": [
                "acquired", "acquisition", "bought", "purchased dealership",
                "merged", "merger"
            ]
        }

        # Product-specific signals (for automotive context)
        self.product_signals = {
            "website": ["website", "web presence", "online", "digital showroom"],
            "crm": ["crm", "customer management", "lead management", "sales pipeline"],
            "marketing": ["marketing", "advertising", "promotion", "email campaigns"],
            "analytics": ["analytics", "reporting", "insights", "metrics", "kpi"],
            "mobile": ["mobile app", "mobile", "app", "smartphone"]
        }

        # Package values (monthly ARR potential)
        self.opportunity_values = {
            "upgrade_basic_to_standard": 250,      # $3K/year
            "upgrade_standard_to_premium": 500,    # $6K/year
            "upgrade_premium_to_enterprise": 1500, # $18K/year
            "add_location": 1000,                  # New location = $12K/year
            "add_module": 300,                     # Additional module = $3.6K/year
            "custom_integration": 2000,            # Custom work = $24K/year
            "team_expansion": 150,                 # Per additional user
        }

    def detect_opportunity(
        self,
        ticket_text: str,
        ticket_subject: str,
        dealer_id: str,
        dealer_name: str,
        current_package: str,
        classification: Dict = None
    ) -> Dict[str, Any]:
        """
        Detect sales opportunities from ticket content.

        Args:
            ticket_text: The ticket description/content
            ticket_subject: The ticket subject line
            dealer_id: Dealer identifier
            dealer_name: Dealer name
            current_package: Current subscription package
            classification: Ticket classification data

        Returns:
            Dictionary with sales opportunity details
        """
        full_text = f"{ticket_subject} {ticket_text}".lower()

        opportunity = {
            "has_opportunity": False,
            "dealer_id": dealer_id,
            "dealer_name": dealer_name,
            "current_package": current_package,
            "opportunity_type": None,
            "signals": [],
            "potential_revenue": 0,
            "confidence": 0,
            "priority": "Low",
            "recommended_action": "",
            "talking_points": [],
            "next_steps": []
        }

        detected_signals = []

        # Check for feature requests
        for category, keywords in self.feature_signals.items():
            for keyword in keywords:
                if keyword in full_text:
                    detected_signals.append({
                        "type": "feature_request",
                        "category": category,
                        "keyword": keyword,
                        "context": self._extract_context(full_text, keyword)
                    })

        # Check for expansion signals
        for category, keywords in self.expansion_signals.items():
            for keyword in keywords:
                if keyword in full_text:
                    detected_signals.append({
                        "type": "expansion",
                        "category": category,
                        "keyword": keyword,
                        "context": self._extract_context(full_text, keyword)
                    })

        # Check for product interest
        for product, keywords in self.product_signals.items():
            for keyword in keywords:
                if keyword in full_text:
                    detected_signals.append({
                        "type": "product_interest",
                        "category": product,
                        "keyword": keyword,
                        "context": self._extract_context(full_text, keyword)
                    })

        # Analyze signals and determine opportunity
        if detected_signals:
            opportunity["has_opportunity"] = True
            opportunity["signals"] = detected_signals

            # Determine opportunity type and value
            signal_categories = [s["category"] for s in detected_signals]
            signal_types = [s["type"] for s in detected_signals]

            # Multi-location opportunity
            if "multi_location" in signal_categories:
                opportunity["opportunity_type"] = "Multi-Location Expansion"
                opportunity["potential_revenue"] = self.opportunity_values["add_location"] * 12
                opportunity["confidence"] = 85
                opportunity["priority"] = "High"
                opportunity["recommended_action"] = "Schedule expansion consultation call"
                opportunity["talking_points"] = [
                    "Customer is expanding to multiple locations",
                    f"Multi-location support available in {current_package if current_package == 'Enterprise' else 'Enterprise'} package",
                    f"Potential: ${opportunity['potential_revenue']:,}/year per additional location",
                    "Centralized management dashboard for all locations"
                ]
                opportunity["next_steps"] = [
                    "Contact within 24 hours to discuss expansion plans",
                    "Prepare multi-location demo and pricing",
                    "Offer migration assistance and onboarding support"
                ]

            # Advanced features request
            elif "advanced_features" in signal_categories:
                if current_package in ["Basic", "Standard"]:
                    opportunity["opportunity_type"] = "Feature Upgrade"
                    if current_package == "Basic":
                        opportunity["potential_revenue"] = self.opportunity_values["upgrade_basic_to_standard"] * 12
                    else:
                        opportunity["potential_revenue"] = self.opportunity_values["upgrade_standard_to_premium"] * 12
                    opportunity["confidence"] = 75
                    opportunity["priority"] = "High"
                    opportunity["recommended_action"] = "Schedule feature demo and upgrade discussion"
                    opportunity["talking_points"] = [
                        f"Customer requesting features available in higher tiers",
                        f"Premium/Enterprise packages include: {', '.join([s['keyword'] for s in detected_signals[:3]])}",
                        f"Upgrade value: ${opportunity['potential_revenue']:,}/year",
                        "Includes priority support and dedicated account manager"
                    ]
                    opportunity["next_steps"] = [
                        "Send feature comparison chart",
                        "Schedule 30-min demo of advanced features",
                        "Provide upgrade pricing with limited-time discount"
                    ]
                else:
                    opportunity["opportunity_type"] = "Custom Integration"
                    opportunity["potential_revenue"] = self.opportunity_values["custom_integration"] * 12
                    opportunity["confidence"] = 60
                    opportunity["priority"] = "Medium"
                    opportunity["recommended_action"] = "Discuss custom development options"

            # Team expansion
            elif "team_expansion" in signal_categories:
                opportunity["opportunity_type"] = "Team Expansion"
                opportunity["potential_revenue"] = self.opportunity_values["team_expansion"] * 12 * 3  # Assume 3 users
                opportunity["confidence"] = 70
                opportunity["priority"] = "Medium"
                opportunity["recommended_action"] = "Discuss team licenses and volume pricing"
                opportunity["talking_points"] = [
                    "Customer is growing their team",
                    "Volume discounts available for 5+ users",
                    "Team collaboration features in Premium+",
                    f"Estimated value: ${opportunity['potential_revenue']:,}/year"
                ]
                opportunity["next_steps"] = [
                    "Provide team pricing breakdown",
                    "Offer demo of collaboration features",
                    "Share team onboarding resources"
                ]

            # Premium support interest
            elif "premium_support" in signal_categories:
                if current_package in ["Basic", "Standard"]:
                    opportunity["opportunity_type"] = "Support Upgrade"
                    opportunity["potential_revenue"] = self.opportunity_values["upgrade_standard_to_premium"] * 12
                    opportunity["confidence"] = 80
                    opportunity["priority"] = "High"
                    opportunity["recommended_action"] = "Highlight Premium/Enterprise support benefits"
                    opportunity["talking_points"] = [
                        "Customer seeking better support experience",
                        "Premium: Priority support with 4-hour response SLA",
                        "Enterprise: Dedicated account manager + phone support",
                        f"Investment: ${opportunity['potential_revenue']:,}/year for peace of mind"
                    ]
                    opportunity["next_steps"] = [
                        "Share support tier comparison",
                        "Offer trial of premium support (1 month)",
                        "Gather specific support pain points"
                    ]

            # Product interest (cross-sell)
            elif "product_interest" in signal_types:
                opportunity["opportunity_type"] = "Cross-Sell Opportunity"
                opportunity["potential_revenue"] = self.opportunity_values["add_module"] * 12
                opportunity["confidence"] = 65
                opportunity["priority"] = "Medium"
                opportunity["recommended_action"] = "Introduce relevant product modules"
                products_of_interest = list(set([s["category"] for s in detected_signals if s["type"] == "product_interest"]))
                opportunity["talking_points"] = [
                    f"Customer showing interest in: {', '.join(products_of_interest)}",
                    "Add-on modules available for current package",
                    f"Estimated value: ${opportunity['potential_revenue']:,}/year",
                    "Bundle pricing available for multiple modules"
                ]
                opportunity["next_steps"] = [
                    "Send product module catalog",
                    "Schedule product demo",
                    "Offer bundle discount"
                ]

            # Expansion/growth signals
            elif "expansion" in signal_types:
                opportunity["opportunity_type"] = "Business Growth"
                opportunity["potential_revenue"] = self.opportunity_values["add_location"] * 12
                opportunity["confidence"] = 70
                opportunity["priority"] = "High"
                opportunity["recommended_action"] = "Discuss scalability and growth plans"
                opportunity["talking_points"] = [
                    "Customer is in growth phase",
                    "Our platform scales with your business",
                    "Enterprise features support rapid expansion",
                    f"Growth package value: ${opportunity['potential_revenue']:,}/year"
                ]
                opportunity["next_steps"] = [
                    "Schedule strategic planning call",
                    "Provide case study of similar growth stories",
                    "Offer growth consultant engagement"
                ]

            # Default for other signals
            else:
                opportunity["opportunity_type"] = "General Interest"
                opportunity["potential_revenue"] = self.opportunity_values["add_module"] * 12
                opportunity["confidence"] = 50
                opportunity["priority"] = "Low"
                opportunity["recommended_action"] = "Follow up to understand needs better"

        return opportunity

    def _extract_context(self, text: str, keyword: str, context_length: int = 50) -> str:
        """
        Extract surrounding context for a detected keyword.

        Args:
            text: Full text
            keyword: The keyword to find
            context_length: Characters to include before/after

        Returns:
            Context string
        """
        idx = text.find(keyword)
        if idx == -1:
            return ""

        start = max(0, idx - context_length)
        end = min(len(text), idx + len(keyword) + context_length)

        context = text[start:end].strip()
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."

        return context

    def get_portfolio_opportunities(self, opportunities: List[Dict]) -> Dict[str, Any]:
        """
        Aggregate sales opportunities across all tickets.

        Args:
            opportunities: List of detected opportunities

        Returns:
            Portfolio-wide sales opportunity summary
        """
        active_opportunities = [o for o in opportunities if o["has_opportunity"]]

        total_potential = sum(o["potential_revenue"] for o in active_opportunities)

        # Group by type
        by_type = {}
        for opp in active_opportunities:
            opp_type = opp["opportunity_type"]
            if opp_type not in by_type:
                by_type[opp_type] = []
            by_type[opp_type].append(opp)

        # Sort by priority and potential revenue
        active_opportunities.sort(
            key=lambda x: (
                {"High": 3, "Medium": 2, "Low": 1}.get(x["priority"], 0),
                x["potential_revenue"]
            ),
            reverse=True
        )

        return {
            "total_opportunities": len(active_opportunities),
            "total_potential_revenue": total_potential,
            "opportunities": active_opportunities,
            "by_type": by_type,
            "high_priority": [o for o in active_opportunities if o["priority"] == "High"],
            "medium_priority": [o for o in active_opportunities if o["priority"] == "Medium"],
            "low_priority": [o for o in active_opportunities if o["priority"] == "Low"]
        }
