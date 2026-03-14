import sys
import os
from neo4j import GraphDatabase

# Configuration matched to your Neo4j Desktop screenshot
URI = "neo4j://127.0.0.1:7687" 
USER = "neo4j"
PASS = "Admin@123$%^" 
CYPHER_FILE = "import.cypher"

def run_import():
    if not os.path.exists(CYPHER_FILE):
        print(f"[-] Error: {CYPHER_FILE} not found.")
        sys.exit(1)

    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    try:
        with driver.session(database="neo4j") as session:
            print("[*] Wiping old graph data...")
            session.run("MATCH (n) DETACH DELETE n")

            with open(CYPHER_FILE, 'r') as f:
                queries = [q.strip() for q in f.read().split(';') if q.strip()]
                
            print(f"[*] Connection successful. Executing {len(queries)} queries...")
            
            with session.begin_transaction() as tx:
                for query in queries:
                    tx.run(query)
                
            print("[+] Success! Graph updated.")
    except Exception as e:
        print(f"[-] FATAL ERROR: {e}")
        sys.exit(1)
    finally:
        driver.close()

if __name__ == "__main__":
    run_import()
