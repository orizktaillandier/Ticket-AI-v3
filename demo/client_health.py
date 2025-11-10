"""
Client Health Score & Churn Prediction System
Analyzes ticket patterns to predict client satisfaction and churn risk
"""
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta
import json
from collections import defaultdict

class ClientHealthEngine:
    """
    Calculates client health scores (0-100) and predicts churn risk.

    Health Score Factors:
    - Ticket volume (increasing = bad)
    - Sentiment trends (declining = bad)
    - Problem frequency (more problems = bad)
    - Urgency indicators (more urgent = bad)
    - Resolution time (longer = bad)
    - Positive interactions (more = good)
    """

    def __init__(self):
        self.dealer_data = {}
        self.historical_tickets = self._load_historical_data()

    def _load_historical_data(self) -> Dict[str, List[Dict]]:
        """
        Load or generate historical ticket data for health scoring.
        In production, this would query the database.
        For demo, we generate realistic patterns.
        """
        try:
            with open("data/historical_tickets.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # Generate mock historical data
            return self._generate_mock_history()

    def _generate_mock_history(self) -> Dict[str, List[Dict]]:
        """Generate realistic historical ticket patterns for 10 dealers"""
        history = {}

        # Dealer 1: Healthy - low volume, positive sentiment
        history["1001"] = [
            {"date": "2025-10-15", "category": "General Question", "sentiment": "Neutral", "tier": "Tier 1"},
            {"date": "2025-10-20", "category": "Product Activation — Existing Client", "sentiment": "Calm", "tier": "Tier 1"},
            {"date": "2025-11-05", "category": "General Question", "sentiment": "Calm", "tier": "Tier 1"},
        ]

        # Dealer 2: Excellent - very low volume, all positive
        history["1002"] = [
            {"date": "2025-10-10", "category": "Product Activation — Existing Client", "sentiment": "Calm", "tier": "Tier 1"},
            {"date": "2025-11-01", "category": "General Question", "sentiment": "Neutral", "tier": "Tier 1"},
        ]

        # Dealer 3: AT RISK - increasing volume, declining sentiment, problems
        history["1003"] = [
            {"date": "2025-10-01", "category": "General Question", "sentiment": "Calm", "tier": "Tier 1"},
            {"date": "2025-10-08", "category": "Product Activation — Existing Client", "sentiment": "Neutral", "tier": "Tier 1"},
            {"date": "2025-10-15", "category": "Problem / Bug", "sentiment": "Concerned", "tier": "Tier 2"},
            {"date": "2025-10-22", "category": "Problem / Bug", "sentiment": "Frustrated", "tier": "Tier 2"},
            {"date": "2025-10-28", "category": "Problem / Bug", "sentiment": "Frustrated", "tier": "Tier 2"},
            {"date": "2025-11-02", "category": "Product Cancellation", "sentiment": "Urgent", "tier": "Tier 3"},
            {"date": "2025-11-05", "category": "Problem / Bug", "sentiment": "Frustrated", "tier": "Tier 2"},
        ]

        # Dealer 4: CRITICAL - multiple problems, urgent, high volume
        history["1004"] = [
            {"date": "2025-10-10", "category": "Problem / Bug", "sentiment": "Concerned", "tier": "Tier 2"},
            {"date": "2025-10-15", "category": "Problem / Bug", "sentiment": "Frustrated", "tier": "Tier 2"},
            {"date": "2025-10-18", "category": "Problem / Bug", "sentiment": "Frustrated", "tier": "Tier 3"},
            {"date": "2025-10-25", "category": "Problem / Bug", "sentiment": "Urgent", "tier": "Tier 3"},
            {"date": "2025-10-30", "category": "Problem / Bug", "sentiment": "Critical", "tier": "Tier 3"},
            {"date": "2025-11-03", "category": "Problem / Bug", "sentiment": "Urgent", "tier": "Tier 3"},
            {"date": "2025-11-06", "category": "Problem / Bug", "sentiment": "Critical", "tier": "Tier 3"},
            {"date": "2025-11-08", "category": "Problem / Bug", "sentiment": "Critical", "tier": "Tier 3"},
        ]

        # Dealer 5: Good - moderate volume, mostly positive
        history["1005"] = [
            {"date": "2025-10-12", "category": "Product Activation — Existing Client", "sentiment": "Calm", "tier": "Tier 1"},
            {"date": "2025-10-20", "category": "General Question", "sentiment": "Neutral", "tier": "Tier 1"},
            {"date": "2025-10-28", "category": "Product Activation — Existing Client", "sentiment": "Neutral", "tier": "Tier 1"},
            {"date": "2025-11-04", "category": "Problem / Bug", "sentiment": "Concerned", "tier": "Tier 2"},
        ]

        # Dealer 6: Fair - some concerns
        history["1006"] = [
            {"date": "2025-10-05", "category": "General Question", "sentiment": "Neutral", "tier": "Tier 1"},
            {"date": "2025-10-18", "category": "Problem / Bug", "sentiment": "Concerned", "tier": "Tier 2"},
            {"date": "2025-10-25", "category": "General Question", "sentiment": "Neutral", "tier": "Tier 1"},
            {"date": "2025-11-01", "category": "Problem / Bug", "sentiment": "Concerned", "tier": "Tier 2"},
            {"date": "2025-11-06", "category": "Problem / Bug", "sentiment": "Frustrated", "tier": "Tier 2"},
        ]

        # Dealer 7: Excellent - very happy client
        history["1007"] = [
            {"date": "2025-10-18", "category": "Product Activation — Existing Client", "sentiment": "Calm", "tier": "Tier 1"},
        ]

        # Dealer 8: Good - new client, onboarding
        history["1008"] = [
            {"date": "2025-10-25", "category": "Product Activation — New Client", "sentiment": "Neutral", "tier": "Tier 2"},
            {"date": "2025-11-02", "category": "General Question", "sentiment": "Calm", "tier": "Tier 1"},
            {"date": "2025-11-05", "category": "Product Activation — Existing Client", "sentiment": "Calm", "tier": "Tier 1"},
        ]

        # Dealer 9: At Risk - declining engagement
        history["1009"] = [
            {"date": "2025-10-01", "category": "Product Activation — Existing Client", "sentiment": "Calm", "tier": "Tier 1"},
            {"date": "2025-10-15", "category": "Problem / Bug", "sentiment": "Concerned", "tier": "Tier 2"},
            {"date": "2025-10-28", "category": "Problem / Bug", "sentiment": "Frustrated", "tier": "Tier 2"},
            {"date": "2025-11-06", "category": "Product Cancellation", "sentiment": "Neutral", "tier": "Tier 1"},
        ]

        # Dealer 10: Healthy - consistent, positive
        history["1010"] = [
            {"date": "2025-10-08", "category": "General Question", "sentiment": "Calm", "tier": "Tier 1"},
            {"date": "2025-10-22", "category": "Product Activation — Existing Client", "sentiment": "Neutral", "tier": "Tier 1"},
            {"date": "2025-11-03", "category": "General Question", "sentiment": "Calm", "tier": "Tier 1"},
        ]

        return history

    def calculate_health_score(self, dealer_id: str) -> Dict[str, Any]:
        """
        Calculate comprehensive health score for a dealer.

        Returns:
            Dictionary with score, factors, trends, and recommendations
        """
        tickets = self.historical_tickets.get(dealer_id, [])

        if not tickets:
            return {
                "score": 75,  # Default for new clients
                "category": "Unknown",
                "color": "gray",
                "tickets_analyzed": 0,
                "factors": {},
                "trend": "stable",
                "recommendations": ["Insufficient data - continue monitoring"]
            }

        # Calculate base score
        base_score = 100
        factors = {}

        # Factor 1: Ticket Volume (last 30 days)
        recent_tickets = [t for t in tickets if self._is_recent(t["date"], days=30)]
        ticket_count = len(recent_tickets)

        if ticket_count > 6:
            volume_penalty = (ticket_count - 6) * 3
            base_score -= min(volume_penalty, 20)
            factors["high_volume"] = -min(volume_penalty, 20)
        elif ticket_count <= 2:
            factors["low_volume"] = 5
            base_score += 5

        # Factor 2: Problem Frequency
        problem_tickets = [t for t in recent_tickets if t["category"] == "Problem / Bug"]
        problem_count = len(problem_tickets)

        if problem_count > 0:
            problem_penalty = problem_count * 8
            base_score -= min(problem_penalty, 30)
            factors["problems"] = -min(problem_penalty, 30)

        # Factor 3: Sentiment Analysis
        negative_sentiments = ["Frustrated", "Urgent", "Critical"]
        negative_count = sum(1 for t in recent_tickets if t["sentiment"] in negative_sentiments)

        if negative_count > 0:
            sentiment_penalty = negative_count * 10
            base_score -= min(sentiment_penalty, 25)
            factors["negative_sentiment"] = -min(sentiment_penalty, 25)

        positive_sentiments = ["Calm"]
        positive_count = sum(1 for t in recent_tickets if t["sentiment"] in positive_sentiments)
        if positive_count > 2:
            factors["positive_sentiment"] = 5
            base_score += 5

        # Factor 4: Urgency Indicators
        urgent_tickets = [t for t in recent_tickets if t["tier"] == "Tier 3"]
        urgent_count = len(urgent_tickets)

        if urgent_count > 0:
            urgency_penalty = urgent_count * 12
            base_score -= min(urgency_penalty, 30)
            factors["urgent_issues"] = -min(urgency_penalty, 30)

        # Factor 5: Cancellation Signals
        cancellation_tickets = [t for t in recent_tickets if t["category"] == "Product Cancellation"]
        if cancellation_tickets:
            base_score -= 15
            factors["cancellation_request"] = -15

        # Factor 6: Trend Analysis (last 15 days vs previous 15 days)
        recent_15 = [t for t in tickets if self._is_recent(t["date"], days=15)]
        previous_15 = [t for t in tickets if self._is_recent(t["date"], days=30) and not self._is_recent(t["date"], days=15)]

        trend = "stable"
        if len(recent_15) > len(previous_15) * 1.5:
            base_score -= 10
            factors["increasing_volume"] = -10
            trend = "declining"
        elif len(recent_15) < len(previous_15) * 0.5 and len(previous_15) > 0:
            base_score += 5
            factors["decreasing_volume"] = 5
            trend = "improving"

        # Ensure score is between 0-100
        final_score = max(0, min(100, base_score))

        # Categorize health
        if final_score >= 90:
            category = "Excellent"
            color = "#22c55e"  # Green
        elif final_score >= 70:
            category = "Good"
            color = "#84cc16"  # Light green
        elif final_score >= 50:
            category = "Fair"
            color = "#eab308"  # Yellow
        elif final_score >= 30:
            category = "At Risk"
            color = "#f97316"  # Orange
        else:
            category = "Critical"
            color = "#ef4444"  # Red

        # Generate recommendations
        recommendations = self._generate_recommendations(final_score, factors, tickets)

        return {
            "score": round(final_score, 1),
            "category": category,
            "color": color,
            "tickets_analyzed": len(tickets),
            "recent_tickets": len(recent_tickets),
            "factors": factors,
            "trend": trend,
            "recommendations": recommendations,
            "problem_count": problem_count,
            "urgent_count": urgent_count
        }

    def predict_churn_risk(self, dealer_id: str, dealer_name: str, arr: float = 0) -> Dict[str, Any]:
        """
        Predict churn probability and calculate revenue at risk.

        Args:
            dealer_id: Dealer ID
            dealer_name: Dealer name
            arr: Annual Recurring Revenue for this client

        Returns:
            Churn prediction with probability, risk level, and intervention suggestions
        """
        health_data = self.calculate_health_score(dealer_id)
        score = health_data["score"]
        tickets = self.historical_tickets.get(dealer_id, [])
        recent_tickets = [t for t in tickets if self._is_recent(t["date"], days=30)]

        # Calculate churn probability based on multiple factors
        churn_probability = 0
        risk_factors = []

        # Factor 1: Health Score (most important)
        if score < 30:
            churn_probability += 60
            risk_factors.append("Critical health score")
        elif score < 50:
            churn_probability += 35
            risk_factors.append("Low health score")
        elif score < 70:
            churn_probability += 15
            risk_factors.append("Below-average health score")

        # Factor 2: Recent problems
        problem_tickets = [t for t in recent_tickets if t["category"] == "Problem / Bug"]
        if len(problem_tickets) >= 3:
            churn_probability += 20
            risk_factors.append(f"{len(problem_tickets)} unresolved problems")

        # Factor 3: Negative sentiment trend
        negative_sentiments = ["Frustrated", "Urgent", "Critical"]
        negative_tickets = [t for t in recent_tickets if t["sentiment"] in negative_sentiments]
        if len(negative_tickets) >= 2:
            churn_probability += 15
            risk_factors.append("Multiple frustrated interactions")

        # Factor 4: Cancellation signals
        cancellation_tickets = [t for t in recent_tickets if t["category"] == "Product Cancellation"]
        if cancellation_tickets:
            churn_probability += 25
            risk_factors.append("Recent cancellation request")

        # Factor 5: Decreasing engagement (bad sign after initial activity)
        if health_data["trend"] == "declining" and len(tickets) > 3:
            churn_probability += 10
            risk_factors.append("Declining engagement")

        # Cap at 95% (never 100% certain)
        churn_probability = min(95, churn_probability)

        # Determine risk level
        if churn_probability >= 70:
            risk_level = "High Risk"
            risk_color = "#ef4444"
            priority = "URGENT"
        elif churn_probability >= 40:
            risk_level = "Medium Risk"
            risk_color = "#f97316"
            priority = "High"
        elif churn_probability >= 10:
            risk_level = "Low Risk"
            risk_color = "#eab308"
            priority = "Monitor"
        else:
            risk_level = "Minimal Risk"
            risk_color = "#22c55e"
            priority = "Stable"

        # Generate intervention strategies
        interventions = self._generate_interventions(churn_probability, risk_factors, health_data)

        # Calculate revenue at risk
        revenue_at_risk = arr * (churn_probability / 100)

        return {
            "dealer_id": dealer_id,
            "dealer_name": dealer_name,
            "churn_probability": round(churn_probability, 1),
            "risk_level": risk_level,
            "risk_color": risk_color,
            "priority": priority,
            "risk_factors": risk_factors,
            "interventions": interventions,
            "arr": arr,
            "revenue_at_risk": round(revenue_at_risk, 0),
            "health_score": score
        }

    def get_all_health_scores(self) -> List[Dict[str, Any]]:
        """Get health scores for all dealers"""
        results = []

        for dealer_id in self.historical_tickets.keys():
            health = self.calculate_health_score(dealer_id)
            health["dealer_id"] = dealer_id
            health["dealer_name"] = f"Dealership_{dealer_id[-1]}"  # Extract number from ID
            results.append(health)

        # Sort by score (worst first)
        results.sort(key=lambda x: x["score"])

        return results

    def _is_recent(self, date_str: str, days: int = 30) -> bool:
        """Check if date is within the last N days"""
        try:
            ticket_date = datetime.strptime(date_str, "%Y-%m-%d")
            cutoff_date = datetime.now() - timedelta(days=days)
            return ticket_date >= cutoff_date
        except:
            return False

    def _generate_recommendations(self, score: float, factors: Dict, tickets: List) -> List[str]:
        """Generate actionable recommendations based on health factors"""
        recommendations = []

        if score < 50:
            recommendations.append("🚨 URGENT: Schedule executive call with client")
            recommendations.append("Review all open issues and create resolution plan")
        elif score < 70:
            recommendations.append("Schedule check-in call with account manager")
            recommendations.append("Proactively address any open concerns")

        if "problems" in factors:
            recommendations.append("Prioritize resolution of outstanding technical issues")

        if "negative_sentiment" in factors:
            recommendations.append("Address client frustration - consider escalation")

        if "urgent_issues" in factors:
            recommendations.append("Review urgent tickets for patterns - may indicate systemic issue")

        if "cancellation_request" in factors:
            recommendations.append("⚠️ Cancellation signal detected - immediate retention strategy needed")

        if "increasing_volume" in factors:
            recommendations.append("Investigate cause of ticket volume increase")

        if not recommendations:
            recommendations.append("Continue monitoring - client is healthy")

        return recommendations

    def _generate_interventions(self, churn_prob: float, risk_factors: List[str], health_data: Dict) -> List[str]:
        """Generate intervention strategies based on churn risk"""
        interventions = []

        if churn_prob >= 70:
            interventions.append("🚨 IMMEDIATE: Executive outreach within 24 hours")
            interventions.append("Offer dedicated support representative")
            interventions.append("Consider service credit or discount")
            interventions.append("Schedule in-person meeting if possible")
        elif churn_prob >= 40:
            interventions.append("Account manager outreach this week")
            interventions.append("Create detailed resolution plan for all issues")
            interventions.append("Increase check-in frequency to weekly")
        elif churn_prob >= 10:
            interventions.append("Proactive check-in from account manager")
            interventions.append("Monitor ticket trends closely")
        else:
            interventions.append("Continue standard support protocols")
            interventions.append("Maintain regular quarterly business reviews")

        return interventions
