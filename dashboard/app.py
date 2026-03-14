import streamlit as st
import streamlit.components.v1 as components
from neo4j import GraphDatabase
from pyvis.network import Network

# --- AURA DB CONNECTION ---
URI = "bolt+ssc://a7c4fec6.databases.neo4j.io" 
USER = "neo4j"
PASS = "pUTM7SqI9HE6H8awExoZK2PKEHznG2sIMFYEaibOwY8" 

st.set_page_config(page_title="Cloud Risk Engine", layout="wide")
st.title("🛡️ Cloud Risk Engine: Attack Path Visualizer")

@st.cache_data
def fetch_graph_data():
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    nodes = {}
    edges = []
    try:
        with driver.session() as session:
            # Query to get Principals and the Roles they are assigned
            query = """
            MATCH (p:Principal)-[a:ASSIGNED]->(r:Role)
            RETURN p.id AS principal, r.name AS role
            LIMIT 50
            """
            result = session.run(query)
            for record in result:
                p = record["principal"]
                r = record["role"]
                
                # Categorize nodes so we can color them differently
                if p not in nodes:
                    nodes[p] = "Principal"
                if r not in nodes:
                    nodes[r] = "Role"
                    
                edges.append((p, r))
    except Exception as e:
        st.error(f"Database connection failed: {e}")
    finally:
        driver.close()
    return nodes, edges

st.markdown("### 🔍 Live Interactive Azure Permission Graph")
st.markdown("*Drag nodes to explore. Hover over Principals to see their full ID.*")

with st.spinner("Rendering Interactive Graph..."):
    nodes_dict, edges = fetch_graph_data()

    if edges:
        # 1. Initialize the interactive network graph
        # Dark background (#0E1117) matches Streamlit's dark mode perfectly
        net = Network(height="600px", width="100%", directed=True, bgcolor="#0E1117", font_color="white")

        # 2. Add nodes with smart formatting
        for node_id, node_type in nodes_dict.items():
            if node_type == "Principal":
                # Fix: Shorten the massive UUIDs for the label so it looks clean
                short_label = node_id[:8] + "..."
                # Color Principals RED to signify potential risk origin points
                net.add_node(node_id, label=short_label, title=f"Principal ID: {node_id}", color="#FF4B4B", shape="dot", size=25)
            else:
                # Color Roles BLUE and make them box-shaped to distinguish them
                net.add_node(node_id, label=node_id, title=f"Azure Role: {node_id}", color="#00B4D8", shape="box")

        # 3. Add the relationships (lines)
        for src, dst in edges:
            net.add_edge(src, dst, color="#555555")

        # 4. Inject physics so the graph "bounces" and spaces itself out automatically
        net.set_options("""
        var options = {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -50,
              "centralGravity": 0.01,
              "springLength": 100,
              "springConstant": 0.08
            },
            "minVelocity": 0.75,
            "solver": "forceAtlas2Based"
          }
        }
        """)

        # 5. Save the interactive graph to an HTML file and embed it in Streamlit
        net.save_graph("pyvis_graph.html")
        with open("pyvis_graph.html", 'r', encoding='utf-8') as HtmlFile:
            source_code = HtmlFile.read()
        
        components.html(source_code, height=650)
        
    else:
        st.warning("No relationship data found. Make sure your Jenkins pipeline pushed the edges to Neo4j!")
