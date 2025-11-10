"""
AI-Powered Dealer Support Ticket Classifier
Hackathon Demo - Fall 2025
"""
import streamlit as st
import json
from datetime import datetime
from classifier import TicketClassifier, load_mock_tickets
from automation_engine import AutomationEngine
from client_health import ClientHealthEngine
from upsell_intelligence import UpsellIntelligence
from sales_intelligence import SalesIntelligence

# Page config
st.set_page_config(
    page_title="AI Ticket Classifier - Demo",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .stButton>button {
        width: 100%;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "classifier" not in st.session_state:
    try:
        st.session_state.classifier = TicketClassifier()
        st.session_state.classifier_ready = True
    except Exception as e:
        st.session_state.classifier_ready = False
        st.session_state.classifier_error = str(e)

if "classifications" not in st.session_state:
    st.session_state.classifications = []

if "sales_opportunities" not in st.session_state:
    st.session_state.sales_opportunities = []

if "mock_tickets" not in st.session_state:
    st.session_state.mock_tickets = load_mock_tickets()

if "automation_engine" not in st.session_state:
    st.session_state.automation_engine = AutomationEngine()

# Header
st.title("🎯 AI-Powered Dealer Support Ticket Classifier")
st.markdown("### Revolutionizing Dealer Retention Through Intelligent Support Automation")

# Check if classifier is ready
if not st.session_state.classifier_ready:
    st.error(f"⚠️ Classifier not ready: {st.session_state.get('classifier_error', 'Unknown error')}")
    st.info("💡 Make sure your `.env` file has `OPENAI_API_KEY` set")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("📊 Demo Stats")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(st.session_state.classifications)}</div>
            <div class="metric-label">Classified</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(st.session_state.mock_tickets)}</div>
            <div class="metric-label">Sample Tickets</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🚀 Key Features")
    st.markdown("""
    - ✅ GPT-5 Powered Classification
    - ✅ Sentiment Analysis
    - ✅ Auto-Response Generation
    - ✅ Key Action Item Extraction
    - ✅ Bilingual Support (EN/FR)
    - ✅ 10-Field Extraction + Tier
    - ✅ Provider & Syndicator Detection
    - ✅ Dealer Database Lookup
    - ✅ 3-Tier Priority System
    """)

    st.markdown("---")
    st.markdown("### 💡 Business Value")
    st.markdown("""
    - **70% faster** ticket routing
    - **Improved dealer satisfaction**
    - **Reduced response times**
    - **Better support metrics**
    """)

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Classify Ticket", "📋 Sample Tickets", "💰 Revenue Impact", "💚 Client Health"])

with tab1:
    st.header("Classify a Support Ticket")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Ticket Input")

        input_method = st.radio(
            "Input Method:",
            ["Direct Text Input", "Load Sample Ticket"],
            horizontal=True
        )

        if input_method == "Load Sample Ticket":
            if st.session_state.mock_tickets:
                ticket_options = [
                    f"{t['ticket_id']} - {t['subject'][:50]}..."
                    for t in st.session_state.mock_tickets
                ]
                selected = st.selectbox("Select a sample ticket:", ticket_options)

                if selected:
                    idx = int(selected.split(" - ")[0]) - 12345
                    if 0 <= idx < len(st.session_state.mock_tickets):
                        ticket = st.session_state.mock_tickets[idx]
                        ticket_subject = st.text_input("Subject:", value=ticket["subject"])
                        ticket_text = st.text_area(
                            "Ticket Content:",
                            value=ticket["description"],
                            height=200
                        )
                    else:
                        ticket_subject = st.text_input("Subject:")
                        ticket_text = st.text_area("Ticket Content:", height=200)
            else:
                st.warning("No sample tickets available")
                ticket_subject = st.text_input("Subject:")
                ticket_text = st.text_area("Ticket Content:", height=200)
        else:
            ticket_subject = st.text_input("Subject:")
            ticket_text = st.text_area(
                "Ticket Content:",
                placeholder="Paste ticket content here...",
                height=200
            )

        classify_button = st.button("🚀 Classify with AI", type="primary")

    with col2:
        st.subheader("Info")
        st.info("""
        **What gets extracted:**

        1. Contact Name
        2. Dealer Name
        3. Dealer ID
        4. Rep Name
        5. Category
        6. Sub-Category
        7. Syndicator (Export)
        8. Provider (Import)
        9. Inventory Type
        10. **Tier Level** (1-3)

        The AI analyzes the ticket and automatically extracts all relevant information.

        **Tier Levels:**
        - **Tier 1:** Simple (automated)
        - **Tier 2:** Human required
        - **Tier 3:** Urgent
        """)

    # Classification
    if classify_button:
        if not ticket_text.strip():
            st.error("Please enter ticket content")
        else:
            with st.spinner("🤖 AI is analyzing the ticket..."):
                result = st.session_state.classifier.classify(ticket_text, ticket_subject)

                if result["success"]:
                    classification = result["classification"]

                    # Get current ticket data (for automation)
                    current_ticket_data = {
                        "subject": ticket_subject,
                        "description": ticket_text,
                        "requester_email": "requester@example.com"  # Default
                    }

                    # If loaded from sample tickets, get the full ticket data
                    if input_method == "Load Sample Ticket" and selected:
                        idx = int(selected.split(" - ")[0]) - 12345
                        if 0 <= idx < len(st.session_state.mock_tickets):
                            sample_ticket = st.session_state.mock_tickets[idx]
                            current_ticket_data["requester_email"] = sample_ticket.get("requester_email", "requester@example.com")

                    # Store for automation
                    st.session_state.current_result = result
                    st.session_state.current_ticket_data = current_ticket_data

                    # Detect sales opportunities
                    if "sales_engine" not in st.session_state:
                        st.session_state.sales_engine = SalesIntelligence()

                    # Get package from revenue data
                    try:
                        with open("data/dealer_revenue.json", "r") as f:
                            revenue_data = json.load(f)
                        dealer_id = classification.get("dealer_id", "Unknown")
                        current_package = revenue_data.get(dealer_id, {}).get("package", "Standard")
                    except:
                        current_package = "Standard"

                    sales_opportunity = st.session_state.sales_engine.detect_opportunity(
                        ticket_text=ticket_text,
                        ticket_subject=ticket_subject,
                        dealer_id=classification.get("dealer_id", "Unknown"),
                        dealer_name=classification.get("dealer_name", "Unknown Dealer"),
                        current_package=current_package,
                        classification=classification
                    )

                    if sales_opportunity["has_opportunity"]:
                        st.session_state.sales_opportunities.append(sales_opportunity)

                    # Store classification
                    st.session_state.classifications.append({
                        "timestamp": datetime.now().isoformat(),
                        "subject": ticket_subject,
                        "classification": classification,
                        "sales_opportunity": sales_opportunity if sales_opportunity["has_opportunity"] else None
                    })

                    # Display success
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.success("✅ Classification Complete!")
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Display results
                    st.subheader("📊 Classification Results")

                    # Highlight tier prominently
                    tier = classification.get("tier", "")
                    tier_colors = {"Tier 1": "🟢", "Tier 2": "🟡", "Tier 3": "🔴"}
                    tier_labels = {"Tier 1": "Simple/Automated", "Tier 2": "Human Required", "Tier 3": "Urgent"}

                    if tier:
                        tier_emoji = tier_colors.get(tier, "⚪")
                        tier_label = tier_labels.get(tier, "Unknown")
                        st.markdown(f"### {tier_emoji} **{tier}** - {tier_label}")
                        st.markdown("---")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Contact Name", classification.get("contact") or "—")
                        st.metric("Dealer Name", classification.get("dealer_name") or "—")
                        st.metric("Dealer ID", classification.get("dealer_id") or "—")

                    with col2:
                        st.metric("Rep", classification.get("rep") or "—")
                        st.metric("Category", classification.get("category") or "—")
                        st.metric("Sub-Category", classification.get("sub_category") or "—")

                    with col3:
                        st.metric("Syndicator (Export)", classification.get("syndicator") or "—")
                        st.metric("Provider (Import)", classification.get("provider") or "—")
                        st.metric("Inventory Type", classification.get("inventory_type") or "—")

                    # AI-Enhanced Features Section
                    st.markdown("---")
                    st.subheader("🤖 AI-Enhanced Insights")

                    col1, col2 = st.columns(2)

                    with col1:
                        # Sentiment Analysis
                        entities = result.get("entities", {})
                        sentiment = entities.get("sentiment", "Neutral")
                        sentiment_colors = {
                            "Calm": ("🟢", "green"),
                            "Neutral": ("🟦", "blue"),
                            "Concerned": ("🟡", "orange"),
                            "Frustrated": ("🟠", "orange"),
                            "Urgent": ("🔴", "red"),
                            "Critical": ("🔴", "red")
                        }
                        emoji, color = sentiment_colors.get(sentiment, ("⚪", "gray"))

                        st.markdown(f"""
                        <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid {color};">
                            <h4>{emoji} Sentiment: {sentiment}</h4>
                            <p style="color: #666; font-size: 0.9rem;">Emotional tone detected from ticket language</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        # Key Action Items
                        key_actions = entities.get("key_action_items", [])
                        if key_actions:
                            action_list = "".join([f"<li>{action}</li>" for action in key_actions[:3]])
                            st.markdown(f"""
                            <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;">
                                <h4>📋 Key Action Items</h4>
                                <ul style="margin-top: 0.5rem; color: #333;">
                                    {action_list}
                                </ul>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;">
                                <h4>📋 Key Action Items</h4>
                                <p style="color: #666; font-size: 0.9rem;">No specific actions detected</p>
                            </div>
                            """, unsafe_allow_html=True)

                    # Suggested Response
                    if result.get("suggested_response"):
                        st.markdown("---")
                        st.subheader("✉️ AI-Generated Response Suggestion")
                        st.markdown("""
                        <div style="background-color: #e8f4f8; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #1f77b4;">
                        """, unsafe_allow_html=True)
                        st.markdown(result["suggested_response"])
                        st.markdown("</div>", unsafe_allow_html=True)

                        # Add copy button hint
                        st.caption("💡 Copy this suggested response to clipboard and customize as needed")

                    # Sales Opportunity Detection
                    if sales_opportunity["has_opportunity"]:
                        st.markdown("---")
                        st.subheader("💰 Sales Opportunity Detected!")

                        # Priority badge
                        priority_colors = {
                            "High": "#dc3545",
                            "Medium": "#ffc107",
                            "Low": "#28a745"
                        }
                        priority_color = priority_colors.get(sales_opportunity["priority"], "#6c757d")

                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 0.5rem; color: white;">
                            <h3 style="margin: 0; color: white;">🎯 {sales_opportunity["opportunity_type"]}</h3>
                            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">Potential Revenue: <strong>${sales_opportunity["potential_revenue"]:,}/year</strong></p>
                            <span style="background-color: {priority_color}; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.9rem; font-weight: bold;">{sales_opportunity["priority"]} Priority</span>
                            <span style="margin-left: 0.5rem; opacity: 0.8;">Confidence: {sales_opportunity["confidence"]}%</span>
                        </div>
                        """, unsafe_allow_html=True)

                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("**🔍 Signals Detected:**")
                            for signal in sales_opportunity["signals"][:5]:
                                st.markdown(f"- {signal['type']}: _{signal['keyword']}_")

                        with col2:
                            st.markdown("**📞 Recommended Action:**")
                            st.markdown(f"> {sales_opportunity['recommended_action']}")

                        if sales_opportunity.get("talking_points"):
                            st.markdown("**💬 Talking Points for Sales Team:**")
                            for point in sales_opportunity["talking_points"]:
                                st.markdown(f"- {point}")

                        if sales_opportunity.get("next_steps"):
                            st.markdown("**✅ Next Steps:**")
                            for step in sales_opportunity["next_steps"]:
                                st.markdown(f"1. {step}")

                    # ============================================================
                    # TIER 1 AUTOMATED RESOLUTION
                    # ============================================================
                    st.markdown("---")
                    st.subheader("⚡ Tier 1 Automated Resolution")

                    # Check if ticket can be automated
                    can_automate, reason = st.session_state.automation_engine.can_automate(
                        classification, result.get("entities", {})
                    )

                    if can_automate:
                        st.success(f"✅ This ticket qualifies for full automation!")
                        st.info(f"**Reason:** {reason}")

                        # Automation button
                        if st.button("🚀 Execute Automated Resolution", type="primary", key="automate_btn"):
                            with st.spinner("🤖 Running automated workflow..."):
                                automation_result = st.session_state.automation_engine.execute_automation(
                                    classification,
                                    result.get("entities", {}),
                                    st.session_state.current_ticket_data
                                )

                                if automation_result["success"]:
                                    st.success(f"🎉 Automation completed in {automation_result['execution_time']}s")

                                    # Display execution log
                                    st.markdown("### 📋 Execution Log")
                                    log_html = '<div style="background-color: #1e1e1e; color: #d4d4d4; padding: 1rem; border-radius: 0.5rem; font-family: monospace; font-size: 0.85rem; max-height: 400px; overflow-y: auto;">'

                                    for entry in automation_result["execution_log"]:
                                        level = entry["level"]
                                        message = entry["message"]
                                        timestamp = entry["timestamp"]

                                        if level == "header":
                                            log_html += f'<div style="color: #4ec9b0; font-weight: bold; margin: 0.5rem 0;">{timestamp} | {message}</div>'
                                        elif level == "step":
                                            log_html += f'<div style="color: #569cd6; font-weight: bold; margin: 0.5rem 0;">{timestamp} | {message}</div>'
                                        elif level == "success":
                                            log_html += f'<div style="color: #4ec9b0; margin: 0.25rem 0 0.25rem 1rem;">{timestamp} | {message}</div>'
                                        elif level == "warning":
                                            log_html += f'<div style="color: #ce9178; margin: 0.25rem 0 0.25rem 1rem;">{timestamp} | {message}</div>'
                                        elif level == "error":
                                            log_html += f'<div style="color: #f48771; margin: 0.25rem 0 0.25rem 1rem;">{timestamp} | {message}</div>'
                                        elif level == "info":
                                            log_html += f'<div style="color: #9cdcfe; margin: 0.25rem 0 0.25rem 1rem;">{timestamp} | {message}</div>'
                                        elif level == "spacer":
                                            log_html += '<div style="margin: 0.5rem 0;"></div>'

                                    log_html += '</div>'
                                    st.markdown(log_html, unsafe_allow_html=True)

                                    # Display emails sent
                                    if automation_result["emails_sent"]:
                                        st.markdown("### ✉️ Emails Sent")
                                        for i, email in enumerate(automation_result["emails_sent"]):
                                            with st.expander(f"📧 {email['type'].replace('_', ' ').title()} - {email['to']} ({email['timestamp']})"):
                                                st.markdown(f"**To:** {email['to']}")
                                                st.markdown(f"**Subject:** {email['subject']}")
                                                st.markdown("**Body:**")
                                                st.text(email['body'])

                                    # Display internal comments
                                    if automation_result["internal_comments"]:
                                        st.markdown("### 💬 Internal Comments")
                                        for comment in automation_result["internal_comments"]:
                                            st.markdown(f"""
                                            <div style="background-color: #fff3cd; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #ffc107; margin: 0.5rem 0;">
                                                <strong>{' '.join(comment['tagged_users'])}</strong> ({comment['timestamp']})<br/>
                                                <pre style="white-space: pre-wrap; margin: 0.5rem 0 0 0;">{comment['comment']}</pre>
                                            </div>
                                            """, unsafe_allow_html=True)

                                    # Display feed configuration
                                    if automation_result.get("feed_configured"):
                                        feed = automation_result["feed_configured"]
                                        st.markdown("### 🔧 Feed Configuration")
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.metric("Feed ID", feed['feed_id'])
                                            st.metric("Feed Type", feed['feed_type'].title())
                                            st.metric("Inventory Type", feed['inventory_type'])
                                        with col2:
                                            st.metric("Status", feed['status'])
                                            st.metric("Dealer ID", feed['dealer_id'])
                                            st.markdown(f"**Feed URL:** `{feed['feed_url']}`")

                                else:
                                    st.error(f"❌ Automation failed: {automation_result.get('error')}")

                    else:
                        st.warning(f"⚠️ This ticket cannot be fully automated")
                        st.info(f"**Reason:** {reason}")
                        st.caption("Manual intervention required - ticket will be routed to appropriate team")

                    # Show JSON
                    with st.expander("🔍 View Classification JSON"):
                        st.json(classification)

                    # Show extracted entities (for debugging/transparency)
                    if result.get("entities"):
                        with st.expander("🤖 View Extracted Entities (AI Phase)"):
                            st.json(result["entities"])

                else:
                    st.error(f"❌ Classification failed: {result.get('error')}")

with tab2:
    st.header("📋 Sample Tickets")
    st.markdown("These are realistic example tickets from our automotive support system.")

    if st.session_state.mock_tickets:
        for ticket in st.session_state.mock_tickets:
            with st.expander(f"🎫 {ticket['ticket_id']} - {ticket['subject']}"):
                st.markdown(f"**Status:** {ticket['status']}")
                st.markdown(f"**Created:** {ticket['created_time']}")
                st.markdown("**Description:**")
                st.text(ticket['description'])

                if ticket.get('threads'):
                    st.markdown("**Threads:**")
                    for thread in ticket['threads']:
                        st.markdown(f"- **{thread['author_name']}:** {thread['content']}")
    else:
        st.warning("No sample tickets loaded")

with tab3:
    st.header("💰 Revenue Impact Dashboard")
    st.markdown("**Real-time financial metrics showing the monetary value of AI-powered ticket automation.**")

    # Load revenue data
    with open("data/dealer_revenue.json", "r") as f:
        revenue_data = json.load(f)

    # Initialize health engine if needed
    if "health_engine" not in st.session_state:
        st.session_state.health_engine = ClientHealthEngine()

    # Calculate portfolio-wide metrics
    total_arr = sum(dealer["arr"] for dealer in revenue_data.values())

    # Calculate churn-related revenue at risk
    revenue_at_risk_churn = 0
    for dealer_id, dealer_info in revenue_data.items():
        health = st.session_state.health_engine.calculate_health_score(dealer_id)
        churn_data = st.session_state.health_engine.predict_churn_risk(
            dealer_id, dealer_info["dealer_name"], dealer_info["arr"]
        )
        revenue_at_risk_churn += churn_data["revenue_at_risk"]

    # Automation cost savings calculations
    # Industry benchmarks:
    # - Manual ticket handling: $25/ticket (30 min @ $50/hr)
    # - Tier 1 (fully automated): $0/ticket
    # - Tier 2 (semi-automated): $10/ticket (12 min @ $50/hr)
    # - Tier 3 (urgent/manual): $25/ticket

    if st.session_state.classifications:
        tier_counts = {
            "Tier 1": len([c for c in st.session_state.classifications if c['classification'].get('tier') == 'Tier 1']),
            "Tier 2": len([c for c in st.session_state.classifications if c['classification'].get('tier') == 'Tier 2']),
            "Tier 3": len([c for c in st.session_state.classifications if c['classification'].get('tier') == 'Tier 3'])
        }

        # Calculate cost savings from automation
        tier1_savings = tier_counts["Tier 1"] * 25  # Full automation saves $25/ticket
        tier2_savings = tier_counts["Tier 2"] * 15  # Partial automation saves $15/ticket
        total_automation_savings = tier1_savings + tier2_savings

        # Project annual savings (assuming current demo rate extrapolates)
        # For demo: assume 5 tickets/day * 365 days = 1,825 tickets/year
        # Tier 1 automation rate
        total_classified = len(st.session_state.classifications)
        tier1_rate = tier_counts["Tier 1"] / total_classified if total_classified > 0 else 0
        tier2_rate = tier_counts["Tier 2"] / total_classified if total_classified > 0 else 0

        annual_tickets = 1825  # Conservative estimate
        annual_tier1_savings = annual_tickets * tier1_rate * 25
        annual_tier2_savings = annual_tickets * tier2_rate * 15
        projected_annual_savings = annual_tier1_savings + annual_tier2_savings

        # Time saved calculations
        tier1_time_saved = tier_counts["Tier 1"] * 30  # 30 min saved per Tier 1 ticket
        tier2_time_saved = tier_counts["Tier 2"] * 18  # 18 min saved per Tier 2 ticket
        total_time_saved_minutes = tier1_time_saved + tier2_time_saved
        total_time_saved_hours = total_time_saved_minutes / 60
    else:
        tier_counts = {"Tier 1": 0, "Tier 2": 0, "Tier 3": 0}
        total_automation_savings = 0
        projected_annual_savings = 0
        total_time_saved_hours = 0
        tier1_rate = 0

    # Revenue protected by preventing churn
    revenue_protected = revenue_at_risk_churn  # Revenue we can save through proactive intervention

    # ============================================================
    # TOP-LINE METRICS
    # ============================================================
    st.markdown("### 🎯 Key Financial Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Portfolio ARR",
            f"${total_arr:,}",
            help="Total Annual Recurring Revenue across all dealers"
        )

    with col2:
        st.metric(
            "Revenue at Risk",
            f"${int(revenue_at_risk_churn):,}",
            delta=f"-{int(revenue_at_risk_churn/total_arr*100)}% of ARR",
            delta_color="inverse",
            help="Revenue at risk from predicted churn"
        )

    with col3:
        st.metric(
            "Automation Savings (Demo)",
            f"${int(total_automation_savings):,}",
            delta=f"{tier1_rate*100:.0f}% Tier 1 rate",
            help="Cost savings from automated ticket handling in this demo session"
        )

    with col4:
        st.metric(
            "Projected Annual Savings",
            f"${int(projected_annual_savings):,}",
            delta=f"{int(total_time_saved_hours)}h saved",
            help="Estimated annual cost savings from automation"
        )

    # ============================================================
    # REVENUE PROTECTION BREAKDOWN
    # ============================================================
    st.markdown("---")
    st.markdown("### 💵 Revenue Protection Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Churn Prevention Impact")
        st.markdown(f"""
        Our AI system identifies at-risk clients before they churn, enabling proactive intervention.

        **Current Status:**
        - Total Revenue at Risk: **${int(revenue_at_risk_churn):,}**
        - Potential Revenue Protected: **${int(revenue_at_risk_churn * 0.7):,}** (70% save rate)
        - Average intervention cost: **$500/client**
        - Net revenue protected: **${int(revenue_at_risk_churn * 0.7 - 500 * 3):,}**

        **ROI on Churn Prevention:** {int((revenue_at_risk_churn * 0.7 - 1500) / 1500 * 100)}x return
        """)

    with col2:
        st.markdown("#### Automation Efficiency Impact")
        st.markdown(f"""
        Intelligent ticket routing and automation reduces operational costs significantly.

        **Current Session:**
        - Tier 1 (Fully Automated): **{tier_counts['Tier 1']} tickets** → ${tier_counts['Tier 1'] * 25:,} saved
        - Tier 2 (Semi-Automated): **{tier_counts['Tier 2']} tickets** → ${tier_counts['Tier 2'] * 15:,} saved
        - Total time saved: **{int(total_time_saved_hours)} hours**

        **Annual Projection:**
        - Estimated annual savings: **${int(projected_annual_savings):,}**
        - FTE time saved: **{int(total_time_saved_hours * 365 / 2080)} positions** (at 2080h/year)
        """)

    # ============================================================
    # UPSELL OPPORTUNITIES
    # ============================================================
    st.markdown("---")
    st.markdown("### 🎯 AI Upsell Intelligence")

    # Initialize upsell engine
    if "upsell_engine" not in st.session_state:
        st.session_state.upsell_engine = UpsellIntelligence()

    # Get ticket histories from health engine
    if "health_engine" in st.session_state:
        # Get all historical data from health engine
        all_histories = st.session_state.health_engine._generate_mock_history()
        ticket_histories = {dealer_id: all_histories.get(dealer_id, []) for dealer_id in revenue_data.keys()}

        # Analyze portfolio for upsell opportunities
        upsell_summary = st.session_state.upsell_engine.get_portfolio_upsell_summary(
            revenue_data,
            ticket_histories
        )

        # Display upsell metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total Upsell Opportunities",
                upsell_summary["total_opportunities"],
                delta=f"${int(upsell_summary['total_potential_revenue']):,} potential",
                help="Number of dealers with identified upsell opportunities"
            )

        with col2:
            high_priority = len(upsell_summary["high_priority"])
            st.metric(
                "High Priority Opportunities",
                high_priority,
                delta="Immediate action recommended",
                delta_color="off",
                help="High-confidence upsell opportunities"
            )

        with col3:
            avg_upsell = upsell_summary['total_potential_revenue'] / upsell_summary['total_opportunities'] if upsell_summary['total_opportunities'] > 0 else 0
            st.metric(
                "Avg Upsell Value",
                f"${int(avg_upsell):,}",
                help="Average additional ARR per upsell opportunity"
            )

        # Display opportunities
        if upsell_summary["total_opportunities"] > 0:
            st.markdown("#### 💰 Top Upsell Opportunities")

            for opp in upsell_summary["opportunities"][:5]:  # Top 5
                priority_color = {
                    "High": "#dc3545",
                    "Medium": "#ffc107",
                    "Low": "#28a745"
                }.get(opp.get("priority", "Low"), "#6c757d")

                with st.expander(
                    f"**{opp['dealer_name']}** | {opp['current_package']} → {opp['recommended_package']} | "
                    f"+${int(opp['revenue_increase']):,}/year",
                    expanded=(opp.get("priority") == "High")
                ):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown(f"""
                        <div style="background-color: rgba(99, 102, 241, 0.05); padding: 1rem; border-radius: 0.5rem; border-left: 4px solid {priority_color};">
                            <p style="margin: 0;"><strong>Priority:</strong> <span style="color: {priority_color};">{opp.get('priority', 'Medium')}</span></p>
                            <p style="margin: 0.5rem 0 0 0;"><strong>Confidence:</strong> {opp.get('confidence', 0)}%</p>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown("**Signals Detected:**")
                        for signal in opp.get("signals_detected", []):
                            signal_emoji = {"expansion": "🏢", "volume": "📈", "features": "⚙️", "growth": "🌱", "support_quality": "🆘"}.get(signal["category"], "💡")
                            st.markdown(f"- {signal_emoji} {signal['category']}: _{signal['keyword']}_")

                        st.markdown("**Reasoning:**")
                        for reason in opp.get("reasoning", []):
                            st.markdown(f"- {reason}")

                    with col2:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 0.5rem; text-align: center; color: white;">
                            <h2 style="margin: 0; color: white;">${int(opp['revenue_increase']):,}</h2>
                            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Additional ARR</p>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"**Current:** ${int(opp['current_arr']):,}/year")
                        st.markdown(f"**Potential:** ${int(opp['potential_arr']):,}/year")

                    if opp.get("talking_points"):
                        st.markdown("**💬 Talking Points for Sales:**")
                        for point in opp["talking_points"]:
                            st.markdown(f"> {point}")

        else:
            st.info("💡 No upsell opportunities detected. All dealers are on optimal packages for their current usage patterns.")

    # ============================================================
    # SALES OPPORTUNITIES FROM TICKETS
    # ============================================================
    st.markdown("---")
    st.markdown("### 🎯 Active Sales Opportunities from Tickets")

    if st.session_state.sales_opportunities:
        # Get portfolio summary
        if "sales_engine" not in st.session_state:
            st.session_state.sales_engine = SalesIntelligence()

        sales_summary = st.session_state.sales_engine.get_portfolio_opportunities(
            st.session_state.sales_opportunities
        )

        # Display metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Sales Opps Detected",
                sales_summary["total_opportunities"],
                help="Revenue opportunities identified from support tickets"
            )

        with col2:
            st.metric(
                "Total Potential Revenue",
                f"${int(sales_summary['total_potential_revenue']):,}",
                help="Combined potential revenue from all detected opportunities"
            )

        with col3:
            high_priority = len(sales_summary["high_priority"])
            st.metric(
                "High Priority",
                high_priority,
                delta="Action required",
                delta_color="off",
                help="High-confidence opportunities requiring immediate follow-up"
            )

        # Display top opportunities
        if sales_summary["total_opportunities"] > 0:
            st.markdown("#### 💎 Top Sales Opportunities")

            for opp in sales_summary["opportunities"][:5]:  # Top 5
                priority_color = {
                    "High": "#dc3545",
                    "Medium": "#ffc107",
                    "Low": "#28a745"
                }.get(opp.get("priority", "Low"), "#6c757d")

                with st.expander(
                    f"**{opp['dealer_name']}** | {opp['opportunity_type']} | +${int(opp['potential_revenue']):,}/year",
                    expanded=(opp.get("priority") == "High")
                ):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown(f"""
                        <div style="background-color: rgba(103, 126, 234, 0.05); padding: 1rem; border-radius: 0.5rem; border-left: 4px solid {priority_color};">
                            <p style="margin: 0;"><strong>Type:</strong> {opp['opportunity_type']}</p>
                            <p style="margin: 0.5rem 0 0 0;"><strong>Priority:</strong> <span style="color: {priority_color};">{opp.get('priority', 'Medium')}</span></p>
                            <p style="margin: 0.5rem 0 0 0;"><strong>Confidence:</strong> {opp.get('confidence', 0)}%</p>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown("**📝 Signals Detected:**")
                        for signal in opp.get("signals", [])[:3]:
                            st.markdown(f"- {signal['type']}: _{signal['keyword']}_")

                        if opp.get("recommended_action"):
                            st.markdown("**📞 Recommended Action:**")
                            st.markdown(f"> {opp['recommended_action']}")

                    with col2:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 1.5rem; border-radius: 0.5rem; text-align: center; color: white;">
                            <h2 style="margin: 0; color: white;">${int(opp['potential_revenue']):,}</h2>
                            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Annual Revenue</p>
                        </div>
                        """, unsafe_allow_html=True)

                    if opp.get("next_steps"):
                        st.markdown("**✅ Next Steps:**")
                        for i, step in enumerate(opp["next_steps"], 1):
                            st.markdown(f"{i}. {step}")
    else:
        st.info("💡 No sales opportunities detected yet. Classify tickets to identify revenue opportunities from customer conversations.")

    # ============================================================
    # AUTOMATION BREAKDOWN
    # ============================================================
    st.markdown("---")
    st.markdown("### ⚡ Automation Performance")

    if st.session_state.classifications:
        col1, col2, col3 = st.columns(3)

        total = sum(tier_counts.values())

        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 0.5rem; text-align: center;">
                <h1 style="color: white; margin: 0;">{tier_counts['Tier 1']}</h1>
                <p style="color: white; margin: 0.5rem 0 0 0;">Tier 1 - Fully Automated</p>
                <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">{tier_counts['Tier 1']/total*100:.0f}% of tickets</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 0.5rem; text-align: center;">
                <h1 style="color: white; margin: 0;">{tier_counts['Tier 2']}</h1>
                <p style="color: white; margin: 0.5rem 0 0 0;">Tier 2 - Semi-Automated</p>
                <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">{tier_counts['Tier 2']/total*100:.0f}% of tickets</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 1.5rem; border-radius: 0.5rem; text-align: center;">
                <h1 style="color: white; margin: 0;">{tier_counts['Tier 3']}</h1>
                <p style="color: white; margin: 0.5rem 0 0 0;">Tier 3 - Manual (Urgent)</p>
                <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">{tier_counts['Tier 3']/total*100:.0f}% of tickets</p>
            </div>
            """, unsafe_allow_html=True)

        # Category breakdown
        st.markdown("---")
        st.markdown("### 📊 Classification Breakdown")

        categories = [c['classification'].get('category') for c in st.session_state.classifications if c['classification'].get('category')]
        category_counts = {}
        for cat in categories:
            category_counts[cat] = category_counts.get(cat, 0) + 1

        if category_counts:
            col1, col2 = st.columns([2, 1])

            with col1:
                for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                    percentage = count / len(categories) * 100
                    st.markdown(f"""
                    <div style="background-color: rgba(99, 102, 241, 0.1); padding: 0.75rem; border-radius: 0.25rem; margin: 0.5rem 0;">
                        <strong>{category}</strong>: {count} tickets ({percentage:.0f}%)
                        <div style="background-color: rgba(99, 102, 241, 0.3); height: 8px; border-radius: 4px; margin-top: 0.5rem;">
                            <div style="background-color: #6366f1; height: 8px; border-radius: 4px; width: {percentage}%;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            with col2:
                st.metric("Total Tickets", len(st.session_state.classifications))
                dealers = [c['classification'].get('dealer_name') for c in st.session_state.classifications if c['classification'].get('dealer_name')]
                st.metric("Unique Dealers", len(set(dealers)))
                st.metric("Avg per Dealer", f"{len(categories)/len(set(dealers)):.1f}" if dealers else "0")

        # Recent classifications
        st.markdown("---")
        st.markdown("### 🕐 Recent Classifications")

        for i, item in enumerate(reversed(st.session_state.classifications[-5:])):
            with st.expander(f"#{len(st.session_state.classifications) - i}: {item['classification'].get('category', 'Unknown')} - {item['classification'].get('dealer_name', 'Unknown Dealer')}"):
                st.markdown(f"**Subject:** {item['subject']}")
                st.markdown(f"**Timestamp:** {item['timestamp']}")
                st.markdown(f"**Tier:** {item['classification'].get('tier', 'N/A')}")
                st.json(item['classification'])
    else:
        st.info("💡 No tickets classified yet. Start classifying tickets to see revenue impact metrics!")

# ============================================================
# TAB 4: CLIENT HEALTH & CHURN PREDICTION
# ============================================================
with tab4:
    st.header("💚 Client Health Dashboard")
    st.markdown("""
    **Predictive analytics to prevent churn and protect revenue.**

    The system analyzes ticket patterns across all clients to calculate health scores (0-100) and predict churn risk.
    This enables **proactive intervention** before clients leave.
    """)

    # Initialize health engine
    if "health_engine" not in st.session_state:
        st.session_state.health_engine = ClientHealthEngine()

    # Load revenue data
    try:
        with open("data/dealer_revenue.json", "r") as f:
            revenue_data = json.load(f)
    except:
        revenue_data = {}

    health_engine = st.session_state.health_engine

    # Get all health scores
    all_health = health_engine.get_all_health_scores()

    # Calculate aggregate metrics
    total_arr = sum(revenue_data.get(h["dealer_id"], {}).get("arr", 0) for h in all_health)
    critical_clients = [h for h in all_health if h["score"] < 30]
    at_risk_clients = [h for h in all_health if 30 <= h["score"] < 50]

    # Calculate revenue at risk
    revenue_at_risk = 0
    for client in critical_clients + at_risk_clients:
        dealer_id = client["dealer_id"]
        arr = revenue_data.get(dealer_id, {}).get("arr", 0)
        churn_data = health_engine.predict_churn_risk(dealer_id, client["dealer_name"], arr)
        revenue_at_risk += churn_data["revenue_at_risk"]

    # Top Metrics
    st.markdown("### 📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total ARR", f"${total_arr:,}")

    with col2:
        st.metric("Revenue at Risk", f"${int(revenue_at_risk):,}", delta=f"-{len(critical_clients + at_risk_clients)} clients", delta_color="inverse")

    with col3:
        st.metric("At Risk Clients", len(at_risk_clients), delta_color="inverse")

    with col4:
        st.metric("Critical Clients", len(critical_clients), delta_color="inverse")

    st.markdown("---")

    # Health Score Distribution
    st.markdown("### 🎯 Client Health Scores")

    # Create color-coded table
    for health in all_health:
        dealer_id = health["dealer_id"]
        dealer_revenue = revenue_data.get(dealer_id, {})
        arr = dealer_revenue.get("arr", 0)

        # Calculate churn prediction
        churn_data = health_engine.predict_churn_risk(dealer_id, health["dealer_name"], arr)

        # Create expandable section for each dealer
        with st.expander(f"**{health['dealer_name']}** | Score: {health['score']}/100 | Health: {health['category']} | ARR: ${arr:,}"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 💚 Health Score")
                st.markdown(f"""
                <div style="background-color: {health['color']}; padding: 1rem; border-radius: 0.5rem; text-align: center;">
                    <h1 style="color: white; margin: 0;">{health['score']}/100</h1>
                    <p style="color: white; margin: 0;"><strong>{health['category']}</strong></p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"**Trend:** {health['trend'].capitalize()}")
                st.markdown(f"**Tickets Analyzed:** {health['tickets_analyzed']} (last 30 days: {health['recent_tickets']})")
                st.markdown(f"**Problems:** {health['problem_count']}")
                st.markdown(f"**Urgent Issues:** {health['urgent_count']}")

                # Show factors
                if health['factors']:
                    st.markdown("**Health Factors:**")
                    for factor, impact in health['factors'].items():
                        emoji = "📉" if impact < 0 else "📈"
                        st.markdown(f"{emoji} {factor.replace('_', ' ').title()}: {impact:+d} points")

            with col2:
                st.markdown("#### 🚨 Churn Risk")
                st.markdown(f"""
                <div style="background-color: {churn_data['risk_color']}; padding: 1rem; border-radius: 0.5rem; text-align: center;">
                    <h1 style="color: white; margin: 0;">{churn_data['churn_probability']}%</h1>
                    <p style="color: white; margin: 0;"><strong>{churn_data['risk_level']}</strong></p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"**Priority:** {churn_data['priority']}")
                st.markdown(f"**Revenue at Risk:** ${int(churn_data['revenue_at_risk']):,}")

                if churn_data['risk_factors']:
                    st.markdown("**Risk Factors:**")
                    for factor in churn_data['risk_factors']:
                        st.markdown(f"⚠️ {factor}")

            # Recommendations
            st.markdown("---")
            st.markdown("#### 💡 Recommended Actions")
            for i, rec in enumerate(health['recommendations'], 1):
                st.markdown(f"{i}. {rec}")

            # Interventions for high-risk clients
            if churn_data['churn_probability'] >= 40:
                st.markdown("---")
                st.markdown("#### 🎯 Intervention Strategy")
                for i, intervention in enumerate(churn_data['interventions'], 1):
                    st.markdown(f"{i}. {intervention}")

    # Summary insights
    st.markdown("---")
    st.markdown("### 🔍 Key Insights")

    if critical_clients:
        st.error(f"🚨 **{len(critical_clients)} CRITICAL clients** require immediate attention!")
        for client in critical_clients[:3]:  # Show top 3
            dealer_id = client["dealer_id"]
            arr = revenue_data.get(dealer_id, {}).get("arr", 0)
            st.markdown(f"- **{client['dealer_name']}** (Score: {client['score']}/100, ARR: ${arr:,})")

    if at_risk_clients:
        st.warning(f"⚠️ **{len(at_risk_clients)} clients at risk** - proactive outreach recommended")

    healthy_clients = [h for h in all_health if h["score"] >= 70]
    if healthy_clients:
        st.success(f"✅ **{len(healthy_clients)} healthy clients** - maintain current support level")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    🤖 Powered by GPT-5 | Built for Cars Commerce Hackathon Fall 2025
</div>
""", unsafe_allow_html=True)
