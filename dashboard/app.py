import streamlit as st
import pandas as pd
from neo4j import GraphDatabase
from streamlit_agraph import agraph, Node, Edge, Config

# --- AURA DB CONNECTION ---
URI = "bolt+ssc://a7c4fec6.databases.neo4j.io" 
USER = "neo4j"
PASS = "pUTM7SqI9HE6H8awExoZK2PKEHznG2sIMFYEaibOwY8" 

st.set_page_config(page_title="Cloud Risk Engine", layout="wide")
st.title("🛡️ Cloud Risk Engine Dashboard")

# --- DATA FETCHING FUNCTIONS ---
@st.cache_data
def fetch_azure_graph_data():
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    nodes_data = {}
    edges_data = []
    try:
        with driver.session() as session:
            query = """
            MATCH (p:Principal)-[a:ASSIGNED]->(r:Role)
            RETURN p.id AS principal_id, 
                   COALESCE(p.principalName, p.displayName, p.name, p.id) AS principal_label, 
                   r.name AS role
            LIMIT 50
            """
            result = session.run(query)
            for record in result:
                p_id = record["principal_id"]
                p_label = record["principal_label"]
                r = record["role"]
                
                if p_id not in nodes_data:
                    nodes_data[p_id] = {"label": p_label, "color": "#FF4B4B"} # Red for Principals
                if r not in nodes_data:
                    nodes_data[r] = {"label": r, "color": "#00B4D8"} # Blue for Roles
                    
                edges_data.append((p_id, r))
    except Exception as e:
        st.error(f"Graph DB connection failed: {e}")
    finally:
        driver.close()
    return nodes_data, edges_data

@st.cache_data
def fetch_mitre_data():
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    mitre_list = []
    try:
        with driver.session() as session:
            query = "MATCH (t:Technique) RETURN t.id AS id, t.name AS name, t.tactic AS tactic"
            result = session.run(query)
            for record in result:
                mitre_list.append({
                    "Technique ID": record["id"],
                    "Name": record["name"],
                    "Tactic (Phase)": record["tactic"]
                })
    except Exception as e:
        st.error(f"Graph DB connection failed: {e}")
    finally:
        driver.close()
    return mitre_list

# --- UI LAYOUT ---
# Create two professional tabs for navigating the dashboard
tab1, tab2 = st.tabs(["🌐 Azure Permission Graph", "📋 MITRE ATT&CK Threats"])

with tab1:
    st.markdown("### Interactive Azure Access Paths")
    st.markdown("*Hover to interact. Drag to rearrange nodes.*")
    
    nodes_dict, edges_list = fetch_azure_graph_data()
    
    if edges_list:
        nodes = []
        edges = []
        
        # 1. Build the Agraph Nodes
        for node_id, data in nodes_dict.items():
            nodes.append( Node(id=node_id, 
                               label=data["label"], 
                               size=25, 
                               color=data["color"]) )
            
        # 2. Build the Agraph Edges
        for src, dst in edges_list:
            edges.append( Edge(source=src, target=dst, color="#888888") )
            
        # 3. Configure the Physics and Layout
        config = Config(width=1000, 
                        height=600, 
                        directed=True,
                        physics=True, 
                        hierarchical=False,
                        nodeHighlightBehavior=True,
                        highlightColor="#F7A7A6")
        
        # 4. Render the interactive graph natively in Streamlit
        return_value = agraph(nodes=nodes, edges=edges, config=config)
    else:
        st.info("No Azure graph data found in Neo4j.")

with tab2:
    st.markdown("### Imported Threat Intelligence (MITRE Framework)")
    st.markdown("*This data is used by the Risk Engine to identify attack escalation paths.*")
    
    mitre_data = fetch_mitre_data()
    
    if mitre_data:
        # Convert the list of dictionaries into a clean Pandas DataFrame
        df = pd.DataFrame(mitre_data)
        
        # Display as an interactive, sortable table
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No MITRE data found in Neo4j. Ensure Stage 4 of the pipeline ran successfully.")
