import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="CI/CD Pipeline Telemetry", page_icon="🚀", layout="wide")
st.title("🚀 GitHub Actions Telemetry Dashboard")
st.markdown("Monitoring pipeline health, build durations, and failure rates.")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('workflow_logs.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except FileNotFoundError:
        st.error("Data not found. Run generate_mock_data.py first!")
        st.stop()

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")
selected_teams = st.sidebar.multiselect("Select Teams", options=df['team'].unique(), default=df['team'].unique())
selected_workflows = st.sidebar.multiselect("Select Workflows", options=df['workflow_name'].unique(), default=df['workflow_name'].unique())

filtered_df = df[(df['team'].isin(selected_teams)) & (df['workflow_name'].isin(selected_workflows))]

# --- TOP LEVEL KPIs ---
total_runs = len(filtered_df)
success_rate = (len(filtered_df[filtered_df['status'] == 'success']) / total_runs) * 100 if total_runs > 0 else 0
avg_duration = filtered_df['duration_seconds'].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Total Workflow Runs", f"{total_runs}")
col2.metric("Pipeline Success Rate", f"{success_rate:.1f}%")
col3.metric("Avg Build Time", f"{avg_duration:.0f}s")

st.divider()

# --- VISUALIZATIONS ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Workflow Status by Team")
    # Grouping data for the bar chart
    team_status = filtered_df.groupby(['team', 'status']).size().reset_index(name='count')
    fig_bar = px.bar(team_status, x='team', y='count', color='status', 
                     color_discrete_map={'success':'#28a745', 'failure':'#dc3545', 'cancelled':'#ffc107'},
                     barmode='group')
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("Build Durations Distribution")
    fig_hist = px.histogram(filtered_df, x="duration_seconds", color="workflow_name", 
                            nbins=30, opacity=0.7)
    st.plotly_chart(fig_hist, use_container_width=True)

st.subheader("Pipeline Executions Over Time")
# Resample by day for a cleaner time series
time_series = filtered_df.set_index('timestamp').resample('D').size().reset_index(name='runs')
fig_line = px.line(time_series, x='timestamp', y='runs', markers=True)
st.plotly_chart(fig_line, use_container_width=True)