"""
AI Upsell Intelligence Engine
Detects revenue opportunities from ticket patterns and dealer behavior
"""

import json
from typing import Dict, List, Any
from datetime import datetime, timedelta


class UpsellIntelligence:
    """
    Analyzes tickets and dealer data to identify upsell opportunities.
    """

    def __init__(self):
        """Initialize the upsell intelligence engine."""
        # Package pricing (monthly)
        self.package_pricing = {
            "Basic": 750,      # $9,000/year
            "Standard": 1000,  # $12,000/year
            "Premium": 1500,   # $18,000/year
            "Enterprise": 3000 # $36,000/year
        }

        # Upsell paths
        self.upsell_paths = {
            "Basic": ["Standard", "Premium", "Enterprise"],
            "Standard": ["Premium", "Enterprise"],
            "Premium": ["Enterprise"],
            "Enterprise": []
        }

        # Growth/expansion signals
        self.growth_signals = {
            "expansion": ["expand", "expansion", "second location", "third location", "new location", "additional location", "multiple location"],
            "volume": ["more api", "api limit", "increase limit", "rate limit", "higher volume", "more calls", "more requests"],
            "features": ["need more features", "advanced features", "premium features", "enterprise features", "custom integration"],
            "growth": ["growing", "growth", "scaling", "scale up", "increase capacity", "add more"],
            "multi_location": ["multi-location", "multiple locations", "all locations", "both locations", "chain"],
            "performance": ["faster", "performance", "speed", "slow", "upgrade performance"],
            "team_size": ["more users", "additional users", "team growth", "more staff", "hiring"]
        }

    def detect_upsell_opportunity(
        self,
        ticket_text: str,
        dealer_id: str,
        dealer_name: str,
        current_package: str,
        current_arr: float,
        ticket_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Detect upsell opportunities from ticket content and behavior patterns.

        Args:
            ticket_text: The ticket description/content
            dealer_id: Dealer identifier
            dealer_name: Dealer name
            current_package: Current subscription package
            current_arr: Current annual recurring revenue
            ticket_history: Historical tickets for pattern analysis

        Returns:
            Dictionary with upsell opportunity details
        """
        opportunity = {
            "has_opportunity": False,
            "confidence": 0,
            "recommended_package": None,
            "current_package": current_package,
            "current_arr": current_arr,
            "potential_arr": current_arr,
            "revenue_increase": 0,
            "signals_detected": [],
            "reasoning": [],
            "priority": "Low",
            "talking_points": []
        }

        # Can't upsell Enterprise (top tier)
        if current_package == "Enterprise":
            opportunity["reasoning"].append("Already on Enterprise package (top tier)")
            return opportunity

        ticket_lower = ticket_text.lower()

        # Detect growth signals in ticket
        signals_found = []
        for category, keywords in self.growth_signals.items():
            for keyword in keywords:
                if keyword in ticket_lower:
                    signals_found.append({
                        "category": category,
                        "keyword": keyword,
                        "type": "explicit"
                    })

        # Analyze signals and determine recommended upgrade
        if signals_found:
            opportunity["has_opportunity"] = True
            opportunity["signals_detected"] = signals_found

            # Determine recommended package based on signals
            signal_categories = [s["category"] for s in signals_found]

            # Enterprise triggers
            if any(cat in signal_categories for cat in ["expansion", "multi_location", "team_size"]):
                recommended = "Enterprise"
                opportunity["confidence"] = 85
                opportunity["priority"] = "High"
                opportunity["reasoning"].append("Multi-location/expansion signals detected - Enterprise recommended")

            # Premium triggers
            elif any(cat in signal_categories for cat in ["volume", "features", "performance"]):
                # If on Basic, recommend Premium
                if current_package == "Basic":
                    recommended = "Premium"
                    opportunity["confidence"] = 75
                    opportunity["priority"] = "Medium"
                    opportunity["reasoning"].append("Feature/volume needs exceed Basic package - Premium recommended")
                # If on Standard, could be Premium or Enterprise
                elif current_package == "Standard":
                    recommended = "Premium"
                    opportunity["confidence"] = 70
                    opportunity["priority"] = "Medium"
                    opportunity["reasoning"].append("Advanced feature requirements - Premium recommended")
                else:
                    recommended = "Premium"
                    opportunity["confidence"] = 60
                    opportunity["priority"] = "Low"

            # Growth triggers (one tier up)
            elif "growth" in signal_categories:
                if current_package == "Basic":
                    recommended = "Standard"
                elif current_package == "Standard":
                    recommended = "Premium"
                else:
                    recommended = "Premium"
                opportunity["confidence"] = 65
                opportunity["priority"] = "Medium"
                opportunity["reasoning"].append("Growth signals indicate need for higher tier")
            else:
                # Default to one tier up
                if current_package == "Basic":
                    recommended = "Standard"
                elif current_package == "Standard":
                    recommended = "Premium"
                else:
                    recommended = "Premium"
                opportunity["confidence"] = 50
                opportunity["priority"] = "Low"

            # Ensure we're actually upgrading
            if recommended in self.upsell_paths.get(current_package, []):
                opportunity["recommended_package"] = recommended

                # Calculate revenue impact
                current_monthly = self.package_pricing[current_package]
                new_monthly = self.package_pricing[recommended]
                monthly_increase = new_monthly - current_monthly
                annual_increase = monthly_increase * 12

                opportunity["potential_arr"] = current_arr + annual_increase
                opportunity["revenue_increase"] = annual_increase

                # Generate talking points
                opportunity["talking_points"] = self._generate_talking_points(
                    current_package,
                    recommended,
                    signal_categories,
                    annual_increase
                )

            else:
                # Recommended package isn't a valid upgrade
                opportunity["has_opportunity"] = False
                opportunity["reasoning"].append(f"{recommended} is not a valid upgrade from {current_package}")

        # Behavioral pattern analysis (if ticket history provided)
        if ticket_history:
            behavioral_opportunity = self._analyze_behavioral_patterns(
                ticket_history,
                current_package,
                current_arr
            )

            if behavioral_opportunity["has_opportunity"]:
                # Merge behavioral insights
                if not opportunity["has_opportunity"] or behavioral_opportunity["confidence"] > opportunity["confidence"]:
                    opportunity.update(behavioral_opportunity)
                else:
                    # Add behavioral signals to existing opportunity
                    opportunity["signals_detected"].extend(behavioral_opportunity.get("signals_detected", []))
                    opportunity["reasoning"].extend(behavioral_opportunity.get("reasoning", []))

        return opportunity

    def _analyze_behavioral_patterns(
        self,
        ticket_history: List[Dict],
        current_package: str,
        current_arr: float
    ) -> Dict[str, Any]:
        """
        Analyze historical ticket patterns to identify upsell opportunities.

        Args:
            ticket_history: List of historical tickets
            current_package: Current package tier
            current_arr: Current ARR

        Returns:
            Upsell opportunity based on behavior patterns
        """
        opportunity = {
            "has_opportunity": False,
            "confidence": 0,
            "recommended_package": None,
            "signals_detected": [],
            "reasoning": []
        }

        # High ticket volume on Basic/Standard = upgrade signal
        recent_tickets = [t for t in ticket_history if t.get("days_ago", 0) <= 30]

        if len(recent_tickets) > 5 and current_package == "Basic":
            opportunity["has_opportunity"] = True
            opportunity["recommended_package"] = "Standard"
            opportunity["confidence"] = 70
            opportunity["priority"] = "Medium"
            opportunity["signals_detected"].append({
                "category": "volume",
                "keyword": f"{len(recent_tickets)} tickets in 30 days",
                "type": "behavioral"
            })
            opportunity["reasoning"].append(f"High ticket volume ({len(recent_tickets)} in 30 days) on Basic package suggests need for Standard")

            # Calculate revenue impact
            current_monthly = self.package_pricing[current_package]
            new_monthly = self.package_pricing["Standard"]
            monthly_increase = new_monthly - current_monthly
            annual_increase = monthly_increase * 12

            opportunity["potential_arr"] = current_arr + annual_increase
            opportunity["revenue_increase"] = annual_increase
            opportunity["talking_points"] = [
                f"High support volume indicates growing business - Standard package offers better support SLAs",
                f"Upgrade to Standard provides priority support and faster response times",
                f"Investment: ${annual_increase:,}/year | Value: Reduced downtime, happier customers"
            ]

        elif len(recent_tickets) > 8 and current_package == "Standard":
            opportunity["has_opportunity"] = True
            opportunity["recommended_package"] = "Premium"
            opportunity["confidence"] = 75
            opportunity["priority"] = "High"
            opportunity["signals_detected"].append({
                "category": "volume",
                "keyword": f"{len(recent_tickets)} tickets in 30 days",
                "type": "behavioral"
            })
            opportunity["reasoning"].append(f"Very high ticket volume ({len(recent_tickets)} in 30 days) suggests need for Premium package with dedicated support")

            # Calculate revenue impact
            current_monthly = self.package_pricing[current_package]
            new_monthly = self.package_pricing["Premium"]
            monthly_increase = new_monthly - current_monthly
            annual_increase = monthly_increase * 12

            opportunity["potential_arr"] = current_arr + annual_increase
            opportunity["revenue_increase"] = annual_increase
            opportunity["talking_points"] = [
                f"Exceptional volume indicates enterprise-scale operations - Premium offers dedicated support manager",
                f"Premium package includes proactive monitoring and custom integrations",
                f"Investment: ${annual_increase:,}/year | ROI: 50% faster issue resolution"
            ]

        # Multiple problem tickets = need better tier
        problem_tickets = [t for t in recent_tickets if t.get("category") == "Problem / Bug"]
        if len(problem_tickets) >= 3:
            if not opportunity["has_opportunity"]:
                # Only create opportunity if there's a valid upgrade path
                if current_package != "Enterprise":
                    opportunity["has_opportunity"] = True
                    opportunity["confidence"] = 65
                    opportunity["priority"] = "Medium"

                    if current_package == "Basic":
                        opportunity["recommended_package"] = "Standard"
                    elif current_package == "Standard":
                        opportunity["recommended_package"] = "Premium"
                    elif current_package == "Premium":
                        opportunity["recommended_package"] = "Enterprise"

                    opportunity["signals_detected"].append({
                        "category": "support_quality",
                        "keyword": f"{len(problem_tickets)} problems in 30 days",
                        "type": "behavioral"
                    })
                    opportunity["reasoning"].append(f"Multiple issues ({len(problem_tickets)}) suggest need for higher-touch support")

                    # Calculate revenue impact
                    if opportunity["recommended_package"]:
                        current_monthly = self.package_pricing[current_package]
                        new_monthly = self.package_pricing[opportunity["recommended_package"]]
                        monthly_increase = new_monthly - current_monthly
                        annual_increase = monthly_increase * 12

                        opportunity["potential_arr"] = current_arr + annual_increase
                        opportunity["revenue_increase"] = annual_increase
                        opportunity["talking_points"] = [
                            f"High issue volume indicates need for {opportunity['recommended_package']} with better support SLAs",
                            f"{opportunity['recommended_package']} package offers faster response times and dedicated support",
                            f"Investment: ${annual_increase:,}/year | Value: Reduced downtime and improved customer satisfaction"
                        ]

        return opportunity

    def _generate_talking_points(
        self,
        current_package: str,
        recommended_package: str,
        signal_categories: List[str],
        revenue_increase: float
    ) -> List[str]:
        """
        Generate sales talking points based on upsell opportunity.

        Args:
            current_package: Current package
            recommended_package: Recommended upgrade
            signal_categories: Categories of signals detected
            revenue_increase: Annual revenue increase

        Returns:
            List of talking points for sales team
        """
        talking_points = []

        # Opening
        talking_points.append(f"Great news - your business is growing! We noticed signals indicating you might benefit from {recommended_package}.")

        # Signal-specific points
        if "expansion" in signal_categories or "multi_location" in signal_categories:
            talking_points.append(f"{recommended_package} is designed for multi-location operations with centralized management and reporting.")
            talking_points.append("Get unified dashboards across all locations + dedicated account manager.")

        if "volume" in signal_categories or "features" in signal_categories:
            talking_points.append(f"{recommended_package} includes higher API limits, advanced features, and priority support.")
            talking_points.append("Unlock custom integrations, webhooks, and advanced analytics.")

        if "performance" in signal_categories:
            talking_points.append(f"{recommended_package} offers 99.9% uptime SLA and dedicated infrastructure.")
            talking_points.append("3x faster response times with dedicated support channel.")

        if "growth" in signal_categories:
            talking_points.append(f"Your growth trajectory suggests you'll outgrow {current_package} soon - {recommended_package} scales with you.")

        # Value proposition
        talking_points.append(f"Investment: ${revenue_increase:,}/year | Typical ROI: 5-8x through increased efficiency and reduced downtime")

        # Call to action
        talking_points.append(f"Let's schedule a 15-min call to show you {recommended_package} features and discuss a smooth transition plan.")

        return talking_points

    def get_portfolio_upsell_summary(self, revenue_data: Dict, ticket_histories: Dict) -> Dict[str, Any]:
        """
        Analyze entire dealer portfolio for upsell opportunities.

        Args:
            revenue_data: Dictionary of dealer revenue data (from dealer_revenue.json)
            ticket_histories: Dictionary of ticket histories per dealer

        Returns:
            Portfolio-wide upsell analysis
        """
        total_upsell_revenue = 0
        opportunities = []

        for dealer_id, dealer_info in revenue_data.items():
            ticket_history = ticket_histories.get(dealer_id, [])

            # Analyze patterns even without explicit ticket text
            if ticket_history:
                behavioral_opp = self._analyze_behavioral_patterns(
                    ticket_history,
                    dealer_info["package"],
                    dealer_info["arr"]
                )

                if behavioral_opp["has_opportunity"]:
                    opportunities.append({
                        "dealer_id": dealer_id,
                        "dealer_name": dealer_info["dealer_name"],
                        "current_package": dealer_info["package"],
                        "current_arr": dealer_info["arr"],
                        **behavioral_opp
                    })
                    total_upsell_revenue += behavioral_opp.get("revenue_increase", 0)

        # Sort by revenue potential
        opportunities.sort(key=lambda x: x.get("revenue_increase", 0), reverse=True)

        return {
            "total_opportunities": len(opportunities),
            "total_potential_revenue": total_upsell_revenue,
            "opportunities": opportunities,
            "high_priority": [o for o in opportunities if o.get("priority") == "High"],
            "medium_priority": [o for o in opportunities if o.get("priority") == "Medium"],
            "low_priority": [o for o in opportunities if o.get("priority") == "Low"]
        }
