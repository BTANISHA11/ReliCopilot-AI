"""Streamlit dashboard for visualizing telemetry data."""

import streamlit as st
import httpx
import pandas as pd
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="ReliCopilot-AI Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Title and description
st.title("🛡️ ReliCopilot-AI Dashboard")
st.markdown("**AI-powered reliability monitoring and failure analysis**")

# Sidebar
st.sidebar.title("Controls")
auto_refresh = st.sidebar.checkbox("Auto-refresh (5s)", value=True)
event_limit = st.sidebar.slider("Events to display", 10, 200, 50)
event_type_filter = st.sidebar.selectbox(
    "Filter by type",
    ["All", "error", "request"]
)

# Function to fetch data from API
@st.cache_data(ttl=5)
def fetch_stats():
    """Fetch statistics from API."""
    try:
        response = httpx.get(f"{API_BASE_URL}/api/stats", timeout=5.0)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Failed to connect to API: {e}")
    return None


@st.cache_data(ttl=5)
def fetch_telemetry(limit=50, event_type=None):
    """Fetch telemetry events from API."""
    try:
        params = {"limit": limit}
        if event_type and event_type != "All":
            params["event_type"] = event_type
        
        response = httpx.get(f"{API_BASE_URL}/api/telemetry", params=params, timeout=5.0)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Failed to connect to API: {e}")
    return None


def trigger_simulation():
    """Trigger a simulated request."""
    try:
        response = httpx.get(f"{API_BASE_URL}/api/simulate", timeout=5.0)
        return response.status_code
    except httpx.HTTPStatusError as e:
        return e.response.status_code
    except Exception:
        return None


# Main dashboard
col1, col2, col3, col4 = st.columns(4)

# Fetch and display stats
stats = fetch_stats()

if stats:
    with col1:
        st.metric("Total Events", stats["total_events"])
    
    with col2:
        st.metric("Error Count", stats["error_count"])
    
    with col3:
        st.metric("Error Rate", f"{stats['error_rate_percent']}%")
    
    with col4:
        st.metric("Avg Latency", f"{stats['avg_latency_ms']:.0f} ms")
else:
    st.warning("⚠️ Unable to connect to API. Make sure the FastAPI server is running on http://localhost:8000")

# Action buttons
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])

with col_btn1:
    if st.button("🎲 Simulate Request", use_container_width=True):
        with st.spinner("Simulating request..."):
            status = trigger_simulation()
            if status:
                if status < 400:
                    st.success(f"✓ Request succeeded (HTTP {status})")
                else:
                    st.error(f"✗ Request failed (HTTP {status})")
                time.sleep(1)
                st.rerun()

with col_btn2:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Telemetry events
st.markdown("---")
st.subheader("📊 Recent Telemetry Events")

telemetry_data = fetch_telemetry(limit=event_limit, event_type=event_type_filter)

if telemetry_data and telemetry_data["events"]:
    events = telemetry_data["events"]
    
    # Create DataFrame for display
    df = pd.DataFrame([
        {
            "ID": e["id"],
            "Timestamp": e["timestamp"][:19],
            "Type": e["event_type"],
            "Endpoint": e["endpoint"],
            "Status": e["status_code"],
            "Latency (ms)": f"{e['latency_ms']:.1f}" if e["latency_ms"] else "N/A",
            "Error": e["error_message"][:50] + "..." if e["error_message"] and len(e["error_message"]) > 50 else (e["error_message"] or "")
        }
        for e in events
    ])
    
    # Display table
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Detailed view of errors with AI analysis
    st.markdown("---")
    st.subheader("🤖 AI Failure Analysis")
    
    error_events = [e for e in events if e["event_type"] == "error"]
    
    if error_events:
        for event in error_events[:5]:  # Show top 5 errors
            with st.expander(f"Event #{event['id']} - {event['endpoint']} (HTTP {event['status_code']})"):
                col_a, col_b = st.columns([1, 2])
                
                with col_a:
                    st.markdown("**Details:**")
                    st.write(f"**Timestamp:** {event['timestamp']}")
                    st.write(f"**Endpoint:** {event['endpoint']}")
                    st.write(f"**Status Code:** {event['status_code']}")
                    st.write(f"**Latency:** {event['latency_ms']:.1f} ms" if event['latency_ms'] else "N/A")
                
                with col_b:
                    st.markdown("**Error Message:**")
                    st.code(event['error_message'], language="text")
                    
                    if event['analysis']:
                        st.markdown("**🤖 AI Analysis:**")
                        st.info(event['analysis'])
                    else:
                        st.warning("No AI analysis available yet")
    else:
        st.success("✓ No errors in recent events")
else:
    st.info("No telemetry data available. Trigger some requests to see data!")

# Auto-refresh
if auto_refresh:
    time.sleep(5)
    st.rerun()
