import streamlit as st
import requests
import time
import json
from datetime import datetime
import logging
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App configuration
st.set_page_config(
    page_title="AI Financial Document Analyzer",
    page_icon="📊",
    layout="wide"
)

API_URL = "http://localhost:8000"

# Initialize session state
if 'current_task_id' not in st.session_state:
    st.session_state.current_task_id = None

def check_backend_health():
    """Check if backend is running."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, {"error": str(e)}

def poll_for_results(task_id: str, max_attempts: int = 60):
    """Poll for analysis results."""
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{API_URL}/analysis/{task_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if data["status"] == "completed":
                    return True, data
                elif data["status"] == "failed":
                    return False, data
                
                # Show progress if available
                if "progress" in data:
                    progress = data["progress"]
                    st.progress(progress.get("current", 0) / progress.get("total", 100))
                    st.text(progress.get("status", "Processing..."))
                
        except Exception as e:
            logger.warning(f"Polling attempt {attempt} failed: {str(e)}")
        
        time.sleep(5)  # Wait 5 seconds between polls
    
    return False, {"error": "Analysis timed out"}

def display_analysis_results(result_data):
    """Display comprehensive analysis results."""
    if not result_data.get("result"):
        st.error("No analysis results available")
        return
    
    analysis = result_data["result"]
    
    # Company Information
    st.subheader("Company Information")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Company:** {analysis.get('company_name', 'Unknown')}")
    with col2:
        st.write(f"**Processing Time:** {result_data.get('processing_time', 'N/A')}")
    
    # Financial Metrics
    st.subheader("Financial Metrics")
    metrics = analysis.get('financial_metrics', {})
    
    if metrics:
        # Create metrics display
        metric_cols = st.columns(4)
        
        with metric_cols[0]:
            if metrics.get('revenue'):
                st.metric("Revenue", f"${metrics['revenue']:,.0f}M")
        
        with metric_cols[1]:
            if metrics.get('net_income'):
                st.metric("Net Income", f"${metrics['net_income']:,.0f}M")
        
        with metric_cols[2]:
            if metrics.get('profit_margin'):
                st.metric("Profit Margin", f"{metrics['profit_margin']:.1f}%")
        
        with metric_cols[3]:
            if metrics.get('eps'):
                st.metric("EPS", f"${metrics['eps']:.2f}")
        
        # Metrics chart
        chart_data = []
        for key, value in metrics.items():
            if value and key in ['revenue', 'net_income', 'operating_cash_flow']:
                chart_data.append({'Metric': key.replace('_', ' ').title(), 'Value': value})
        
        if chart_data:
            df = pd.DataFrame(chart_data)
            fig = px.bar(df, x='Metric', y='Value', title='Key Financial Metrics ($ Millions)')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No financial metrics extracted")
    
    # Investment Recommendations
    st.subheader("Investment Recommendations")
    recommendations = analysis.get('investment_recommendations', [])
    
    if recommendations:
        for i, rec in enumerate(recommendations):
            with st.expander(f"Recommendation {i+1}: {rec.get('action', 'N/A').upper()}"):
                st.write(f"**Asset:** {rec.get('asset', 'N/A')}")
                st.write(f"**Risk Level:** {rec.get('risk_level', 'N/A')}")
                st.write(f"**Confidence:** {rec.get('confidence', 0):.0%}")
                st.write(f"**Rationale:** {rec.get('rationale', 'N/A')}")
    else:
        st.info("No specific recommendations generated")
    
    # Risk Assessment
    st.subheader("Risk Assessment")
    risks = analysis.get('risk_assessments', [])
    
    if risks:
        for risk in risks:
            level = risk.get('level', 'Medium')
            color = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}.get(level, 'gray')
            
            st.markdown(f"**{risk.get('category', 'Risk')}** - :{color}[{level}]")
            st.write(f"**Description:** {risk.get('description', 'N/A')}")
            st.write(f"**Mitigation:** {risk.get('mitigation', 'N/A')}")
            st.markdown("---")
    else:
        st.info("Standard market risks apply")
    
    # Market Insights
    if analysis.get('market_insights'):
        st.subheader("Market Insights")
        for insight in analysis['market_insights']:
            st.write(f"• {insight}")
    
    # Summary
    if analysis.get('summary'):
        st.subheader("Analysis Summary")
        st.write(analysis['summary'])
    
    # Query-specific response
    if analysis.get('query_response'):
        st.subheader("Your Query Response")
        st.write(analysis['query_response'])

# Main UI
st.title("AI Financial Document Analyzer")
st.subheader("Upload financial documents for AI-powered investment analysis")

# Check backend status
backend_available, health_data = check_backend_health()

if not backend_available:
    st.error("⚠️ Backend services unavailable. Please start the API server.")
    st.code("python main.py")
    st.stop()

st.success("✅ AI Analysis System Online")

# File upload section
uploaded_file = st.file_uploader(
    "Upload Financial Document (PDF)", 
    type=["pdf"],
    help="Upload quarterly reports, annual reports, 10-K, 10-Q, or other financial documents"
)

# Analysis query
analysis_queries = [
    "Comprehensive financial analysis and investment recommendation",
    "Risk assessment and mitigation strategies", 
    "Growth potential and competitive analysis",
    "Cash flow and liquidity analysis",
    "Valuation and pricing analysis"
]

selected_query = st.selectbox("Analysis Type:", analysis_queries)

# Custom query option
with st.expander("Custom Analysis Query"):
    custom_query = st.text_area(
        "Enter specific analysis requirements:",
        placeholder="e.g., Focus on debt levels and cash flow sustainability...",
        height=80
    )

final_query = custom_query.strip() if custom_query.strip() else selected_query

# Analysis buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Fast Analysis (30 seconds)", type="primary"):
        if not uploaded_file:
            st.error("Please upload a PDF file first")
        else:
            with st.spinner("Running AI analysis..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    data = {"query": final_query}
                    
                    response = requests.post(f"{API_URL}/analyze-fast", files=files, data=data, timeout=120)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Analysis Complete!")
                        display_analysis_results(result)
                    else:
                        st.error(f"Analysis failed: {response.text}")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with col2:
    if st.button("🔄 Queued Analysis (comprehensive)"):
        if not uploaded_file:
            st.error("Please upload a PDF file first")
        else:
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                data = {"query": final_query}
                
                response = requests.post(f"{API_URL}/analyze", files=files, data=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.current_task_id = result["task_id"]
                    st.success("✅ Analysis queued! Tracking progress...")
                    st.rerun()
                else:
                    st.error(f"Failed to queue analysis: {response.text}")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Progress tracking for queued analysis
if st.session_state.current_task_id:
    st.subheader("Analysis Progress")
    
    with st.spinner("Analyzing document..."):
        success, result_data = poll_for_results(st.session_state.current_task_id)
        
        if success:
            st.success("✅ Comprehensive Analysis Complete!")
            display_analysis_results(result_data)
            st.session_state.current_task_id = None
        else:
            st.error(f"Analysis failed: {result_data.get('error', 'Unknown error')}")
            st.session_state.current_task_id = None

# Analysis history
st.subheader("Recent Analyses")
try:
    response = requests.get(f"{API_URL}/analyses?limit=5", timeout=10)
    if response.status_code == 200:
        data = response.json()
        
        for analysis in data["analyses"]:
            with st.expander(f"📄 {analysis['filename']} - {analysis['status']}"):
                st.write(f"**Query:** {analysis['query'][:100]}...")
                st.write(f"**Date:** {analysis['created_at'][:19]}")
                
                if analysis['status'] == 'completed' and st.button(f"View Results", key=analysis['task_id']):
                    # Display results for this analysis
                    display_analysis_results(analysis)
                    
except Exception as e:
    st.warning("Could not load analysis history")