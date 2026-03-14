import sys
import os
from neo4j import GraphDatabase

# CRITICAL: Must start with 'bolt://' or 'neo4j://'
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
        with driver.session() as session:
            # 1. Clear existing data to prevent duplicates
            print("[*] Wiping old graph data...")
            session.run("MATCH (n) DETACH DELETE n")

            # 2. Load the new data
            with open(CYPHER_FILE, 'r') as f:
                # Filter out lines like ':begin' or ':commit' which are for cypher-shell
                queries = [q.strip() for q in f.read().split(';') if q.strip() and not q.startswith(':')]
                
            print(f"[*] Connection successful. Executing {len(queries)} queries...")
            
            with session.begin_transaction() as tx:
                for query in queries:
                    tx.run(query)
                
            # 3. Quick verification count
            result = session.run("MATCH (n) RETURN count(n) AS count")
            count = result.single()["count"]
            print(f"[+] Success! Graph updated with {count} nodes.")

    except Exception as e:
        print(f"[-] Connection Failed: {e}")
        print("TIP: Make sure the 'Start' button (Green) is clicked in Neo4j Desktop.")
        sys.exit(1)
    finally:
        driver.close()

if __name__ == "__main__":
    run_import()
