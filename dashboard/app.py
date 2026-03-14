import streamlit as st
import pandas as pd
from neo4j import GraphDatabase
from streamlit_agraph import agraph, Node, Edge, Config

URI = "bolt+ssc://a7c4fec6.databases.neo4j.io" 
USER = "neo4j"
PASS = "pUTM7SqI9HE6H8awExoZK2PKEHznG2sIMFYEaibOwY8" 

st.set_page_config(page_title="Cloud Risk Engine", layout="wide")
st.title("🛡️ Cloud Risk Engine Dashboard")

@st.cache_data
def fetch_data():
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    nodes_data, edges_data, mitre_data = {}, [], []
    try:
        with driver.session() as session:
            # 1. Fetch Graph Data
            graph_res = session.run("""
                MATCH (p:Principal)-[:ASSIGNED]->(r:Role)
                RETURN p.id as id, COALESCE(p.displayName, p.id) as name, r.name as role
                LIMIT 50
            """)
            for rec in graph_res:
                nodes_data[rec['id']] = {"label": rec['name'], "color": "#FF4B4B"}
                nodes_data[rec['role']] = {"label": rec['role'], "color": "#00B4D8"}
                edges_data.append((rec['id'], rec['role']))

            # 2. Fetch MITRE Data
            mitre_res = session.run("MATCH (t:Technique) RETURN t.id as id, t.name as name, t.tactic as tactic")
            for rec in mitre_res:
                mitre_data.append({"ID": rec['id'], "Name": rec['name'], "Tactic": rec['tactic']})
                
    finally: driver.close()
    return nodes_data, edges_data, mitre_data

nodes_dict, edges_list, mitre_list = fetch_data()

tab1, tab2 = st.tabs(["🌐 Azure Permission Graph", "📋 MITRE ATT&CK Threats"])

with tab1:
    if edges_list:
        nodes = [Node(id=k, label=v['label'], size=25, color=v['color']) for k,v in nodes_dict.items()]
        edges = [Edge(source=s, target=t) for s,t in edges_list]
        config = Config(width=1000, height=600, physics=True)
        agraph(nodes=nodes, edges=edges, config=config)
    else:
        st.warning("⚠️ No graph data found. Did you run the ingestion scripts?")

with tab2:
    if mitre_list:
        st.dataframe(pd.DataFrame(mitre_list), use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ No MITRE threats found in database.")

# --- DEBUG SECTION (Visible only if you scroll down) ---
with st.expander("🛠️ Debug Info"):
    st.write(f"Nodes found: {len(nodes_dict)}")
    st.write(f"Edges found: {len(edges_list)}")
    st.write(f"MITRE Rows: {len(mitre_list)}")
