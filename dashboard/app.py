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

# --- IMPROVED DATA FETCHING ---

@st.cache_data
def fetch_azure_graph_data():
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    nodes_data = {}
    edges_data = []
    try:
        with driver.session() as session:
            # We use COALESCE to try multiple property names in order of preference
            query = """
            MATCH (p:Principal)-[a:ASSIGNED]->(r:Role)
            RETURN p.id AS principal_id, 
                   COALESCE(p.displayName, p.principalName, p.name, p.id) AS principal_label, 
                   r.name AS role
            LIMIT 100
            """
            result = session.run(query)
            for record in result:
                p_id = record["principal_id"]
                p_label = record["principal_label"]
                r_name = record["role"]
                
                if p_id not in nodes_data:
                    nodes_data[p_id] = {"label": p_label, "color": "#FF4B4B"}
                if r_name not in nodes_data:
                    nodes_data[r_name] = {"label": r_name, "color": "#00B4D8"}
                    
                edges_data.append((p_id, r_name))
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
            # Adjust these keys to match exactly what is in your mitre_mapping.json
            query = """
            MATCH (t:Technique) 
            RETURN t.id AS tid, t.name AS tname, t.tactic AS ttactic
            """
            result = session.run(query)
            for record in result:
                mitre_list.append({
                    "Technique ID": record["tid"],
                    "Name": record["tname"],
                    "Tactic (Phase)": record["ttactic"]
                })
    except Exception as e:
        st.error(f"MITRE Fetch failed: {e}")
    finally:
        driver.close()
    return mitre_list
