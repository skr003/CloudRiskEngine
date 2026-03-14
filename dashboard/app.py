import streamlit as st
from neo4j import GraphDatabase

# --- AURA DB CONNECTION ---
URI = "bolt+ssc://a7c4fec6.databases.neo4j.io" 
USER = "neo4j"
PASS = "PASTE_YOUR_NEW_PASSWORD_HERE"

st.set_page_config(page_title="Cloud Risk Engine", layout="wide")
st.title("🛡️ Cloud Risk Engine Dashboard")

@st.cache_data
def fetch_risk_data():
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    risks = []
    try:
        with driver.session() as session:
            # Simple query to grab Azure Roles
            result = session.run("MATCH (r:Role) RETURN r.name AS role LIMIT 5")
            for record in result:
                risks.append(record["role"])
    except Exception as e:
        st.error(f"Database connection failed: {e}")
    finally:
        driver.close()
    return risks

st.subheader("High-Risk Azure Roles in Environment")
roles = fetch_risk_data()

if roles:
    for role in roles:
        st.warning(f"Detected Role: {role}")
else:
    st.success("No roles found or still loading...")
