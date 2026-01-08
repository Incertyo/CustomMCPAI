"""
Modern AI Cloud Optimization Dashboard - Apple/Google Style
"""

import streamlit as st
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import OptimizationDB
import httpx

# Page configuration
st.set_page_config(
    page_title="Cloud Optimization AI",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark Minimalist Style with Monospace (Apple/Google-inspired)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');
    
    /* Global */
    .stApp {
        background: #0f172a;
        color: #e2e8f0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    .stApp pre, code, .mono { font-family: 'JetBrains Mono', monospace; }
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Header */
    .minimal-header {
        padding: 2rem 0 1rem 0;
        border-bottom: 1px solid #1f2937;
        margin-bottom: 3rem;
        background: transparent;
    }
    .minimal-header h1 {
        font-size: 2rem; font-weight: 600; color: #e5e7eb; margin: 0; letter-spacing: -0.5px;
    }
    .minimal-header p {
        font-size: 0.9rem; color: #94a3b8; margin: 0.5rem 0 0 0; font-weight: 400;
    }
    
    /* Cards */
    .clean-card, .rec-minimal, .chat-container, .stat-minimal, .chart-box {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 1.25rem;
        transition: all 0.2s;
        box-shadow: 0 8px 24px rgba(0,0,0,0.35);
    }
    .clean-card:hover, .rec-minimal:hover, .chart-box:hover {
        border-color: #3b82f6;
        box-shadow: 0 12px 32px rgba(59,130,246,0.15);
    }
    
    /* Stats */
    .stat-minimal { text-align: left; padding: 1rem; }
    .stat-value { font-size: 2rem; font-weight: 600; color: #e5e7eb; margin: 0.2rem 0; letter-spacing: -0.5px; }
    .stat-label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.6px; font-weight: 600; margin-bottom: 0.4rem; }
    .stat-change { font-size: 0.85rem; color: #22c55e; font-family: 'JetBrains Mono', monospace; }
    
    /* Recommendations */
    .rec-id {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #94a3b8;
        background: #0b1220;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 0.4rem;
    }
    .rec-title-minimal { font-size: 1rem; font-weight: 600; color: #e5e7eb; margin: 0 0 0.4rem 0; }
    .rec-savings { font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; font-weight: 600; color: #4ade80; margin: 0.3rem 0; }
    .badge-minimal {
        display: inline-block; padding: 0.25rem 0.7rem; border-radius: 6px; font-size: 0.75rem;
        font-weight: 600; font-family: 'Inter', sans-serif; margin-right: 0.4rem; margin-top: 0.4rem;
    }
    .badge-low { background: #064e3b; color: #bbf7d0; }
    .badge-medium { background: #78350f; color: #fef3c7; }
    .badge-high { background: #7f1d1d; color: #fecdd3; }
    .badge-type { background: #1e293b; color: #bfdbfe; border: 1px solid #334155; }
    
    /* Chat */
    .chat-container { height: 500px; display: flex; flex-direction: column; }
    .chat-message { margin-bottom: 0.75rem; padding: 0.75rem 1rem; border-radius: 10px; max-width: 80%; }
    .chat-user { background: #3b82f6; color: white; margin-left: auto; text-align: right; }
    .chat-bot { background: #0b1220; color: #e5e7eb; border: 1px solid #1f2937; }
    
    /* Buttons & Inputs */
    .stButton > button {
        border-radius: 10px; border: 1px solid #1f2937; padding: 0.5rem 1rem;
        font-weight: 600; font-family: 'Inter', sans-serif; background: #111827; color: #e5e7eb;
        transition: all 0.2s;
    }
    .stButton > button:hover { border-color: #3b82f6; box-shadow: 0 6px 18px rgba(59,130,246,0.25); }
    .stTextInput > div > div > input { font-family: 'JetBrains Mono', monospace; color: #e5e7eb; background: #0b1220; border: 1px solid #1f2937; }
    .stSelectbox label { font-size: 0.9rem; color: #cbd5e1; font-weight: 600; }
    
    /* Info / Alerts */
    .stInfo { background: #0b1220; border-left: 3px solid #3b82f6; border-radius: 8px; color: #e2e8f0; }
    .stSuccess { background: #0b1220; color: #4ade80; }
    .stError { background: #0b1220; color: #f87171; }
    
    /* Code blocks */
    pre { background: #0b1220; border: 1px solid #1f2937; border-radius: 10px; padding: 1rem; font-family: 'JetBrains Mono', monospace; font-size: 0.88rem; color: #e5e7eb; }
    
    /* Divider */
    .divider { height: 1px; background: #1f2937; margin: 2rem 0; }
    
    /* Charts wrapper */
    .chart-box { margin-top: 0.5rem; }
    
    /* Fade-out animation for dismissed cards */
    @keyframes fadeOut {
        0% {opacity: 1; transform: translateY(0); max-height: 400px;}
        100% {opacity: 0; transform: translateY(-6px) scale(0.98); max-height: 0; margin: 0; padding: 0;}
    }
    .rec-hidden { animation: fadeOut 0.35s ease forwards; overflow: hidden; }
    </style>
""", unsafe_allow_html=True)


def load_recommendations_from_db(db: OptimizationDB, limit: int = 50, status: str = None, resource_type: str = None) -> list:
    """Load recommendations from database"""
    recs = db.get_recommendations(limit=limit)
    if status and status != "All":
        recs = [r for r in recs if r.get("status") == status]
    if resource_type and resource_type != "All":
        recs = [r for r in recs if r.get("resource_type") == resource_type]
    return recs


def export_to_csv(db: OptimizationDB, filename: str = None):
    """Export recommendations to CSV"""
    recs = db.get_recommendations(limit=1000)
    df = pd.DataFrame(recs)
    if filename is None:
        filename = f"cloud_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return df.to_csv(index=False), filename


def export_to_json(db: OptimizationDB, filename: str = None):
    """Export recommendations to JSON"""
    recs = db.get_recommendations(limit=1000)
    sessions = db.get_analysis_sessions(limit=100)
    data = {
        "exported_at": datetime.now().isoformat(),
        "recommendations": recs,
        "analysis_sessions": sessions
    }
    if filename is None:
        filename = f"cloud_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return json.dumps(data, indent=2, default=str), filename


def query_ai_agent(query: str) -> str:
    """Query the AI agent for optimization advice"""
    try:
        # Simple rule-based responses (can be enhanced with actual AI)
        query_lower = query.lower()
        
        if "cost" in query_lower or "save" in query_lower or "expensive" in query_lower:
            return "To reduce costs, I recommend:\n1. Right-size underutilized instances\n2. Move infrequent data to cold storage\n3. Use reserved instances for steady workloads\n4. Clean up unused snapshots and volumes\n\nWould you like me to analyze your specific resources?"
        
        elif "performance" in query_lower or "slow" in query_lower or "speed" in query_lower:
            return "For performance optimization:\n1. Upgrade instances with high CPU/memory usage\n2. Optimize database queries\n3. Use CDN for static content\n4. Implement auto-scaling\n\nI can analyze your current performance metrics if you'd like."
        
        elif "security" in query_lower or "secure" in query_lower:
            return "Security best practices:\n1. Enable encryption at rest and in transit\n2. Use IAM roles with least privilege\n3. Enable CloudTrail/audit logging\n4. Regular security updates\n5. Network segmentation\n\nWould you like specific security recommendations?"
        
        elif "monitor" in query_lower or "alert" in query_lower:
            return "Monitoring recommendations:\n1. Set up CloudWatch/Monitoring dashboards\n2. Configure cost anomaly alerts\n3. Monitor resource utilization\n4. Track spending trends\n\nI can help set up custom alerts."
        
        else:
            return f"I understand you're asking about: '{query}'\n\nI can help with:\n• Cost optimization\n• Performance tuning\n• Security recommendations\n• Resource right-sizing\n• Monitoring setup\n\nWhat specific area would you like to optimize?"
    
    except Exception as e:
        return f"Error processing query: {str(e)}"


def main():
    """Main Streamlit app"""
    
    # Initialize database
    db = OptimizationDB()
    
    # Minimalist Header
    st.markdown("""
        <div class="minimal-header">
            <h1>Cloud Optimization</h1>
            <p>AI-powered infrastructure optimization and cost management</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Main Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Recommendations", "AI Assistant", "Export"])
    
    with tab1:
        # Statistics Row
        stats = db.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class="stat-minimal">
                    <div class="stat-label">Total Savings</div>
                    <div class="stat-value">${stats['total_savings']:.0f}</div>
                    <div class="stat-change">per month</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="stat-minimal">
                    <div class="stat-label">Recommendations</div>
                    <div class="stat-value">{stats['total_recommendations']}</div>
                    <div class="stat-change" style="color: #6b7280;">found</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            pending = stats['by_status'].get('pending', 0)
            st.markdown(f"""
                <div class="stat-minimal">
                    <div class="stat-label">Pending</div>
                    <div class="stat-value">{pending}</div>
                    <div class="stat-change" style="color: #f59e0b;">review</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            approved = stats['by_status'].get('approved', 0)
            st.markdown(f"""
                <div class="stat-minimal">
                    <div class="stat-label">Approved</div>
                    <div class="stat-value">{approved}</div>
                    <div class="stat-change" style="color: #10b981;">implemented</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if stats["by_type"]:
                st.markdown('<h3 class="section-title-minimal">By Resource Type</h3>', unsafe_allow_html=True)
                fig_type = px.pie(
                    values=list(stats["by_type"].values()),
                    names=list(stats["by_type"].keys()),
                    color_discrete_sequence=['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
                )
                fig_type.update_layout(
                    height=300,
                    plot_bgcolor='#0b1220',
                    paper_bgcolor='#0b1220',
                    font=dict(size=11, color='#e5e7eb', family='Inter'),
                    showlegend=True,
                    margin=dict(l=0, r=0, t=0, b=0),
                    legend=dict(font=dict(color='#e5e7eb'))
                )
                st.plotly_chart(fig_type, use_container_width=True)
        
        with col2:
            if stats["by_risk"]:
                st.markdown('<h3 class="section-title-minimal">By Risk Level</h3>', unsafe_allow_html=True)
                fig_risk = px.bar(
                    x=list(stats["by_risk"].keys()),
                    y=list(stats["by_risk"].values()),
                    color=list(stats["by_risk"].keys()),
                    color_discrete_map={
                        "low": "#10b981",
                        "medium": "#f59e0b",
                        "high": "#ef4444"
                    }
                )
                fig_risk.update_layout(
                    height=300,
                    plot_bgcolor='#0b1220',
                    paper_bgcolor='#0b1220',
                    font=dict(size=11, color='#e5e7eb', family='Inter'),
                    showlegend=False,
                    xaxis_title="",
                    yaxis_title="",
                    margin=dict(l=0, r=0, t=0, b=0),
                    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', color='#e5e7eb'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', color='#e5e7eb')
                )
                st.plotly_chart(fig_risk, use_container_width=True)
        
        # Historical Trend
        sessions = db.get_analysis_sessions(limit=20)
        if sessions:
            st.markdown('<h3 class="section-title-minimal">Savings Trend</h3>', unsafe_allow_html=True)
            df_sessions = pd.DataFrame(sessions)
            df_sessions['timestamp'] = pd.to_datetime(df_sessions['timestamp'])
            df_sessions = df_sessions.sort_values('timestamp')
            
            fig_trend = px.line(
                df_sessions,
                x='timestamp',
                y='total_savings',
                markers=True
            )
            fig_trend.update_layout(
                height=300,
                plot_bgcolor='#0b1220',
                paper_bgcolor='#0b1220',
                font=dict(size=11, color='#e5e7eb', family='Inter'),
                xaxis_title="",
                yaxis_title="",
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)', color='#e5e7eb'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)', color='#e5e7eb')
            )
            fig_trend.update_traces(line_color='#3b82f6', line_width=2, marker_size=6)
            st.plotly_chart(fig_trend, use_container_width=True)
    
    with tab2:
        st.markdown('<h3 class="section-title-minimal">Optimization Recommendations</h3>', unsafe_allow_html=True)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Status", ["All", "pending", "approved", "rejected"], key="status_filter")
        with col2:
            resource_filter = st.selectbox("Resource Type", ["All", "compute", "storage", "network"], key="resource_filter")
        with col3:
            risk_filter = st.selectbox("Risk Level", ["All", "low", "medium", "high"], key="risk_filter")
        
        # Load recommendations
        recommendations = load_recommendations_from_db(
            db, 
            limit=50,
            status=status_filter if status_filter != "All" else None,
            resource_type=resource_filter if resource_filter != "All" else None
        )
        
        if risk_filter != "All":
            recommendations = [r for r in recommendations if r.get("risk", "").lower() == risk_filter.lower()]
        
        # Track dismissed cards for smooth transition
        if "dismissed_recs" not in st.session_state:
            st.session_state.dismissed_recs = set()

        if not recommendations:
            st.info("No recommendations found. Run the AI agent to generate recommendations.")
        else:
            st.caption(f"Showing {len(recommendations)} recommendations")
            
            for rec in recommendations:
                resource_id = rec.get("resource_id", "Unknown")
                risk = rec.get("risk", "low").lower()
                priority = rec.get("priority", "medium").lower()
                resource_type = rec.get("resource_type", "unknown").lower()
                savings = rec.get("estimated_savings", 0)
                if isinstance(savings, (int, float)):
                    savings_str = f"${savings:.2f}/month"
                else:
                    savings_str = str(savings)
                
                rec_id = rec.get("id", 0)
                
                hidden_class = "rec-hidden" if rec_id in st.session_state.dismissed_recs else ""

                st.markdown(f"""
                    <div class="rec-minimal {hidden_class}">
                        <div class="rec-id">{resource_id}</div>
                        <div class="rec-title-minimal">{rec.get('issue', 'N/A')}</div>
                        <div class="rec-savings">{savings_str}</div>
                        <div>
                            <span class="badge-minimal badge-{risk}">{risk.upper()}</span>
                            <span class="badge-minimal" style="background: #e0e7ff; color: #3730a3;">{resource_type.upper()}</span>
                        </div>
                        <p style="color: #cbd5e1; font-size: 0.875rem; margin-top: 0.75rem; line-height: 1.5;">
                            <strong>Action:</strong> {rec.get('action', 'N/A')}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 1, 4])
                with col1:
                    if st.button("Approve", key=f"approve_{rec_id}", use_container_width=True):
                        db.approve_recommendation(rec_id)
                        st.session_state.dismissed_recs.add(rec_id)
                        st.success("Approved")
                with col2:
                    if st.button("Reject", key=f"reject_{rec_id}", use_container_width=True):
                        db.reject_recommendation(rec_id)
                        st.session_state.dismissed_recs.add(rec_id)
                        st.info("Rejected")
                with col3:
                    st.caption(f"Effort: {rec.get('implementation_effort', 'N/A').title()}")

    
    with tab3:
        st.markdown('<h3 class="section-title-minimal">AI Optimization Assistant</h3>', unsafe_allow_html=True)
        st.caption("Ask me anything about cloud optimization, cost savings, or performance tuning")
        
        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [
                {"role": "bot", "message": "Hello! I'm your AI Cloud Optimization Assistant. I can help you:\n\n• Optimize costs\n• Improve performance\n• Enhance security\n• Right-size resources\n\nWhat would you like to optimize today?"}
            ]
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f"""
                        <div style="text-align: right; margin-bottom: 1rem;">
                            <div style="background: #3b82f6; color: white; padding: 0.75rem 1rem; border-radius: 8px; display: inline-block; max-width: 70%;">
                                {msg['message']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style="text-align: left; margin-bottom: 1rem;">
                            <div style="background: #f3f4f6; color: #111827; padding: 0.75rem 1rem; border-radius: 8px; display: inline-block; max-width: 70%; font-family: 'Inter', sans-serif;">
                                {msg['message'].replace(chr(10), '<br>')}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        
        # Chat input
        col1, col2 = st.columns([5, 1])
        with col1:
            user_query = st.text_input(
                "Ask a question...",
                key="chat_input",
                placeholder="e.g., How can I reduce my cloud costs?",
                label_visibility="collapsed"
            )
        with col2:
            send_button = st.button("Send", use_container_width=True)
        
        if send_button and user_query:
            # Add user message
            st.session_state.chat_history.append({"role": "user", "message": user_query})
            
            # Get AI response
            response = query_ai_agent(user_query)
            st.session_state.chat_history.append({"role": "bot", "message": response})
            
            st.rerun()
        
        # Quick action buttons
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.5rem;">Quick actions:</p>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("💰 Cost Optimization", use_container_width=True):
                query = "How can I reduce my cloud costs?"
                st.session_state.chat_history.append({"role": "user", "message": query})
                st.session_state.chat_history.append({"role": "bot", "message": query_ai_agent(query)})
                st.rerun()
        with col2:
            if st.button("⚡ Performance", use_container_width=True):
                query = "How can I improve performance?"
                st.session_state.chat_history.append({"role": "user", "message": query})
                st.session_state.chat_history.append({"role": "bot", "message": query_ai_agent(query)})
                st.rerun()
        with col3:
            if st.button("🔒 Security", use_container_width=True):
                query = "What are security best practices?"
                st.session_state.chat_history.append({"role": "user", "message": query})
                st.session_state.chat_history.append({"role": "bot", "message": query_ai_agent(query)})
                st.rerun()
        with col4:
            if st.button("📊 Analyze", use_container_width=True):
                st.info("Run: python gemini_agent.py to generate new analysis")
    
    with tab4:
        st.markdown('<h3 class="section-title-minimal">Export Data</h3>', unsafe_allow_html=True)
        st.caption("Export your optimization recommendations and analysis data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### CSV Export")
            st.caption("Export recommendations as CSV file")
            csv_data, csv_filename = export_to_csv(db)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=csv_filename,
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            st.markdown("### JSON Export")
            st.caption("Export full data including sessions")
            json_data, json_filename = export_to_json(db)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=json_filename,
                mime="application/json",
                use_container_width=True
            )
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Statistics Summary
        st.markdown("### Export Summary")
        stats = db.get_statistics()
        
        summary_data = {
            "Total Recommendations": stats["total_recommendations"],
            "Total Potential Savings": f"${stats['total_savings']:.2f}/month",
            "Analysis Sessions": stats["total_sessions"],
            "By Status": stats["by_status"],
            "By Resource Type": stats["by_type"],
            "By Risk Level": stats["by_risk"]
        }
        
        st.json(summary_data)
        
        # Preview data
        with st.expander("Preview Recommendations"):
            recs = db.get_recommendations(limit=10)
            if recs:
                df_preview = pd.DataFrame(recs)
                st.dataframe(df_preview[["resource_id", "resource_type", "issue", "estimated_savings", "risk", "status"]], use_container_width=True)


if __name__ == "__main__":
    main()
