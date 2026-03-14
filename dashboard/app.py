import streamlit as st
from neo4j import GraphDatabase
import networkx as nx
import matplotlib.pyplot as plt

# --- AURA DB CONNECTION ---
URI = "bolt+ssc://a7c4fec6.databases.neo4j.io" 
USER = "neo4j"
PASS = "pUTM7SqI9HE6H8awExoZK2PKEHznG2sIMFYEaibOwY8" 

st.set_page_config(page_title="Cloud Risk Engine", layout="wide")
st.title("🛡️ Cloud Risk Engine: Attack Path Visualizer")

@st.cache_data
def fetch_graph_data():
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    nodes = set()
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
                nodes.add(p)
                nodes.add(r)
                edges.append((p, r))
    except Exception as e:
        st.error(f"Database connection failed: {e}")
    finally:
        driver.close()
    return list(nodes), edges

st.markdown("### 🔍 Live Azure Permission Graph")

with st.spinner("Querying Neo4j Aura Database..."):
    nodes, edges = fetch_graph_data()

    if edges:
        # Create a NetworkX directed graph
        G = nx.DiGraph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)

        # Plotting the graph
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Spring layout spaces the nodes out nicely
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        
        # Draw nodes and edges
        nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=2000, alpha=0.8, ax=ax)
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=8, font_family="sans-serif", ax=ax)

        plt.axis('off') # Hide the grid lines
        st.pyplot(fig)  # Send the plot to the Streamlit web page
        
    else:
        st.warning("No relationship data found. Make sure your Jenkins pipeline pushed the edges to Neo4j!")
