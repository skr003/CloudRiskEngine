import streamlit as st
import pandas as pd
import json
import os

# Page Config
st.set_page_config(page_title="CIEM Risk Dashboard", layout="wide")

# Constants
JSON_FILE = "output/mitre_mapping_with_name.json"

def load_data():
    """Loads the analysis JSON file into a Pandas DataFrame."""
    if not os.path.exists(JSON_FILE):
        return None
    
    try:
        with open(JSON_FILE, 'r') as f:
            data = json.load(f)
        
        if not data:
            return pd.DataFrame()
            
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return pd.DataFrame()

# --- Main Layout ---
st.title("🛡️ Identity Risk & Escalation Dashboard")
st.markdown("Analysis of **User → Role → Dangerous Action → MITRE TTP** paths.")

df = load_data()

if df is None:
    st.error(f"File not found: `{JSON_FILE}`. Please run the import pipeline first.")
    st.stop()

if df.empty:
    st.warning("No risks found in the analysis file! (This is good news, or the mapping failed.)")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Filters")
selected_role = st.sidebar.multiselect("Filter by Role", options=df["Role"].unique())
selected_ttp = st.sidebar.multiselect("Filter by MITRE ID", options=df["MitreID"].unique())

# Apply Filters
df_filtered = df.copy()
if selected_role:
    df_filtered = df_filtered[df_filtered["Role"].isin(selected_role)]
if selected_ttp:
    df_filtered = df_filtered[df_filtered["MitreID"].isin(selected_ttp)]

# --- Metrics Section ---
col1, col2, col3 = st.columns(3)
col1.metric("Risky Identities", df_filtered["User"].nunique())
col2.metric("Unique Vulnerabilities (TTPs)", df_filtered["MitreID"].nunique())
col3.metric("Total Paths Detected", len(df_filtered))

st.divider()

# --- Visualizations ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("🚨 Top Risky Users")
    # Count number of dangerous permissions per user
    user_risk = df_filtered["User"].value_counts().reset_index()
    user_risk.columns = ["User", "Risk Count"]
    st.dataframe(user_risk, hide_index=True, use_container_width=True)

with c2:
    st.subheader("📉 Top Escalation Techniques")
    # Count occurrences of each TTP
    ttp_counts = df_filtered["MitreID"].value_counts().reset_index()
    ttp_counts.columns = ["MITRE ID", "Frequency"]
    st.bar_chart(ttp_counts.set_index("MITRE ID"))

st.divider()

# --- Detailed Data Table ---
st.subheader("🔍 Detailed Escalation Paths")
st.dataframe(
    df_filtered,
    use_container_width=True,
    column_config={
        "MitreID": st.column_config.TextColumn("MITRE ID", help="The attack technique ID"),
        "DangerousPermission": st.column_config.TextColumn("Permission", width="medium"),
    }
)

# Download Button
csv = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Report as CSV",
    data=csv,
    file_name='risk_analysis_report.csv',
    mime='text/csv',
)
