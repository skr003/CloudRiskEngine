import streamlit as st
import pandas as pd
from neo4j import GraphDatabase

# Config
uri = "bolt://localhost:7687"
user = "neo4j"
password = os.getenv("NEO4J_PASSWORD", "test123") # Read from Env

st.title("🛡️ CIEM Risk Dashboard")

@st.cache_resource
def get_driver():
    return GraphDatabase.driver(uri, auth=(user, password))

driver = get_driver()

st.header("High Risk Identities (Privilege Escalation)")

query = """
MATCH (u:Principal)-[:ASSIGNED]->(r:Role)-[:ALLOWS_TECHNIQUE]->(t:TTP)
RETURN u.id AS User, r.name AS Role, t.id AS TTP, count(t) as RiskScore
ORDER BY RiskScore DESC LIMIT 20
"""

with driver.session() as session:
    result = session.run(query)
    data = [r.data() for r in result]
    df = pd.DataFrame(data)

if not df.empty:
    st.dataframe(df)
    st.bar_chart(df.set_index("User")["RiskScore"])
else:
    st.success("No critical risks found.")
