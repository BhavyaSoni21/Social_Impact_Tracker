"""
Streamlit Dashboard for Social Impact Tracker
Interactive visualization and data entry interface
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from frontend.utils import format_currency, format_number, format_percentage, get_api_url

# Page configuration
st.set_page_config(
    page_title="Social Impact Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    </style>
""", unsafe_allow_html=True)

# API base URL
API_BASE_URL = get_api_url()


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def fetch_analytics_summary():
    """Fetch summary analytics from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/summary")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching analytics: {e}")
        return None


def fetch_ranked_programs():
    """Fetch ranked programs from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/ranked?limit=20")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching ranked programs: {e}")
        return []


def fetch_trends():
    """Fetch trend data from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/trends")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching trends: {e}")
        return []


def fetch_programs():
    """Fetch all programs from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/programs?limit=1000")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching programs: {e}")
        return []


def submit_program(program_data):
    """Submit new program to API"""
    try:
        response = requests.post(f"{API_BASE_URL}/programs", json=program_data)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.HTTPError as e:
        error_detail = e.response.json().get("detail", str(e))
        return None, error_detail
    except Exception as e:
        return None, str(e)


def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('<div class="main-header">📊 Social Impact Tracker</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Check API health
    if not check_api_health():
        st.error("⚠️ Cannot connect to API. Please ensure the backend is running on http://localhost:8000")
        st.info("Run: `uvicorn backend.main:app --reload`")
        return
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Add Program", "View Programs", "Analytics"])
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Add Program":
        show_add_program()
    elif page == "View Programs":
        show_programs_list()
    elif page == "Analytics":
        show_analytics()


def show_dashboard():
    """Display main dashboard with summary metrics and charts"""
    
    st.header("📈 Dashboard Overview")
    
    # Fetch data
    summary = fetch_analytics_summary()
    
    if not summary:
        st.warning("No data available. Add some programs to get started!")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Programs",
            value=format_number(summary['total_programs']),
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Beneficiaries",
            value=format_number(summary['total_beneficiaries']),
            delta=None
        )
    
    with col3:
        st.metric(
            label="Average Impact Score",
            value=f"{summary['average_impact_score']:.1f}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Total Cost",
            value=format_currency(summary['total_cost']),
            delta=None
        )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Top Programs by Impact Score")
        ranked = fetch_ranked_programs()
        if ranked:
            df_ranked = pd.DataFrame(ranked)
            fig = px.bar(
                df_ranked.head(10),
                x='composite_impact_score',
                y='program_name',
                orientation='h',
                title='Top 10 Programs',
                labels={'composite_impact_score': 'Impact Score', 'program_name': 'Program'},
                color='composite_impact_score',
                color_continuous_scale='Blues'
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Cost vs Outcome Improvement")
        programs = fetch_programs()
        if programs:
            df_programs = pd.DataFrame(programs)
            df_programs['outcome_improvement'] = df_programs['post_outcome_score'] - df_programs['pre_outcome_score']
            
            fig = px.scatter(
                df_programs,
                x='cost',
                y='outcome_improvement',
                size='beneficiaries',
                color='outcome_improvement',
                hover_data=['program_name'],
                title='Cost vs Impact',
                labels={'cost': 'Program Cost ($)', 'outcome_improvement': 'Outcome Improvement'},
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Beneficiary growth trend
    st.subheader("📈 Beneficiary Growth Trend")
    trends = fetch_trends()
    if trends:
        df_trends = pd.DataFrame(trends)
        
        fig = px.line(
            df_trends,
            x='time_period',
            y='beneficiaries',
            title='Beneficiary Growth Over Time',
            labels={'time_period': 'Time Period', 'beneficiaries': 'Number of Beneficiaries'},
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)


def show_add_program():
    """Display form to add new program"""
    
    st.header("➕ Add New Program")
    
    with st.form("program_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            program_name = st.text_input("Program Name *", placeholder="e.g., Youth Education Initiative")
            time_period = st.text_input("Time Period *", placeholder="e.g., 2025-Q1")
            beneficiaries = st.number_input("Number of Beneficiaries *", min_value=1, value=100, step=1)
        
        with col2:
            cost = st.number_input("Total Cost ($) *", min_value=0.01, value=10000.00, step=100.00, format="%.2f")
            pre_outcome = st.slider("Pre-Outcome Score *", min_value=0.0, max_value=100.0, value=40.0, step=0.1)
            post_outcome = st.slider("Post-Outcome Score *", min_value=0.0, max_value=100.0, value=70.0, step=0.1)
        
        submitted = st.form_submit_button("Submit Program", use_container_width=True)
        
        if submitted:
            # Validate inputs
            if not program_name or not time_period:
                st.error("Please fill in all required fields")
                return
            
            if post_outcome < pre_outcome - 10:
                st.warning("Post-outcome score is significantly lower than pre-outcome score. Are you sure?")
            
            # Prepare data
            program_data = {
                "program_name": program_name,
                "time_period": time_period,
                "beneficiaries": beneficiaries,
                "cost": cost,
                "pre_outcome_score": pre_outcome,
                "post_outcome_score": post_outcome
            }
            
            # Submit to API
            result, error = submit_program(program_data)
            
            if error:
                st.error(f"Error: {error}")
            else:
                st.success(f"✅ Program '{program_name}' added successfully!")
                st.balloons()
                
                # Show computed metrics
                if result:
                    st.info("Program created successfully. View it in the 'View Programs' or 'Dashboard' section.")


def show_programs_list():
    """Display list of all programs"""
    
    st.header("📋 All Programs")
    
    programs = fetch_programs()
    
    if not programs:
        st.info("No programs found. Add your first program to get started!")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(programs)
    
    # Add computed columns
    df['outcome_improvement'] = df['post_outcome_score'] - df['pre_outcome_score']
    df['cost_per_beneficiary'] = df['cost'] / df['beneficiaries']
    
    # Format for display
    display_df = df[[
        'id', 'program_name', 'time_period', 'beneficiaries', 
        'cost', 'outcome_improvement', 'cost_per_beneficiary'
    ]].copy()
    
    display_df.columns = [
        'ID', 'Program Name', 'Time Period', 'Beneficiaries',
        'Cost ($)', 'Outcome Improvement', 'Cost per Beneficiary ($)'
    ]
    
    # Format numbers
    display_df['Cost ($)'] = display_df['Cost ($)'].apply(lambda x: f"${x:,.2f}")
    display_df['Cost per Beneficiary ($)'] = display_df['Cost per Beneficiary ($)'].apply(lambda x: f"${x:,.2f}")
    display_df['Outcome Improvement'] = display_df['Outcome Improvement'].apply(lambda x: f"{x:.1f}")
    
    # Display with filtering
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.info(f"📊 Total: {len(programs)} programs")


def show_analytics():
    """Display detailed analytics"""
    
    st.header("📊 Detailed Analytics")
    
    # Ranked programs table
    st.subheader("🏆 Program Rankings by Impact Score")
    ranked = fetch_ranked_programs()
    
    if ranked:
        df_ranked = pd.DataFrame(ranked)
        
        # Format for display
        display_ranked = df_ranked[[
            'program_name', 'outcome_improvement', 
            'cost_per_beneficiary', 'growth_rate', 'composite_impact_score'
        ]].copy()
        
        display_ranked.columns = [
            'Program Name', 'Outcome Improvement', 
            'Cost/Beneficiary ($)', 'Growth Rate', 'Impact Score'
        ]
        
        display_ranked['Cost/Beneficiary ($)'] = display_ranked['Cost/Beneficiary ($)'].apply(lambda x: f"${x:,.2f}")
        display_ranked['Growth Rate'] = display_ranked['Growth Rate'].apply(
            lambda x: format_percentage(x) if pd.notna(x) else "N/A"
        )
        display_ranked['Outcome Improvement'] = display_ranked['Outcome Improvement'].apply(lambda x: f"{x:.1f}")
        display_ranked['Impact Score'] = display_ranked['Impact Score'].apply(lambda x: f"{x:.1f}")
        
        st.dataframe(display_ranked, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Distribution charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Impact Score Distribution")
        if ranked:
            fig = px.histogram(
                df_ranked,
                x='composite_impact_score',
                nbins=20,
                title='Distribution of Impact Scores',
                labels={'composite_impact_score': 'Impact Score'},
                color_discrete_sequence=['#1f77b4']
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💵 Cost Efficiency Analysis")
        if ranked:
            fig = px.box(
                df_ranked,
                y='cost_per_beneficiary',
                title='Cost per Beneficiary Distribution',
                labels={'cost_per_beneficiary': 'Cost per Beneficiary ($)'},
                color_discrete_sequence=['#2ca02c']
            )
            st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
