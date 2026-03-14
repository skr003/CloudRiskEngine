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
            # Cypher Update: COALESCE grabs the first property that isn't null.
            # It tries principalName, then displayName, then name. 
            # If all fail, it falls back to the raw ID.
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
                
                # Store the friendly label inside our dictionary
                if p_id not in nodes:
                    nodes[p_id] = {"type": "Principal", "label": p_label}
                if r not in nodes:
                    nodes[r] = {"type": "Role", "label": r}
                    
                # The relationship is still drawn between the unique IDs
                edges.append((p_id, r))
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
        net = Network(height="600px", width="100%", directed=True, bgcolor="#0E1117", font_color="white")

        # Update how nodes are added to the graph using the new friendly labels
        for node_id, node_data in nodes_dict.items():
            if node_data["type"] == "Principal":
                # Now it displays 'sudharshan@domain.com' but keeps the UUID in the hover title!
                net.add_node(node_id, label=node_data["label"], title=f"Principal ID: {node_id}", color="#FF4B4B", shape="dot", size=25)
            else:
                net.add_node(node_id, label=node_data["label"], title=f"Azure Role: {node_id}", color="#00B4D8", shape="box")

        for src, dst in edges:
            net.add_edge(src, dst, color="#555555")

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

        net.save_graph("pyvis_graph.html")
        with open("pyvis_graph.html", 'r', encoding='utf-8') as HtmlFile:
            source_code = HtmlFile.read()
        
        components.html(source_code, height=650)
        
    else:
        st.warning("No relationship data found. Make sure your Jenkins pipeline pushed the edges to Neo4j!")
