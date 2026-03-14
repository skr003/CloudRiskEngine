import sys
import os
from neo4j import GraphDatabase

# Using 127.0.0.1 is more stable for Neo4j Desktop on Windows than 'localhost'
URI = "bolt://127.0.0.1:7687" 
USER = "neo4j"
PASS = "Admin@123$%^" # Ensure this matches the password you set in Neo4j Desktop
CYPHER_FILE = "import.cypher"

def run_import():
    if not os.path.exists(CYPHER_FILE):
        print(f"Error: {CYPHER_FILE} not found.")
        sys.exit(1)

    # The driver initiation
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    try:
        with driver.session() as session:
            with open(CYPHER_FILE, 'r') as f:
                # We split by semicolon but ignore the :begin/:commit lines 
                # because the Python driver handles transactions natively
                queries = [q.strip() for q in f.read().split(';') if q.strip() and not q.startswith(':')]
                
                print(f"[*] Connection successful. Found {len(queries)} queries.")
                
                # We wrap everything in one transaction for speed
                with session.begin_transaction() as tx:
                    for query in queries:
                        tx.run(query)
                
        print("[+] Graph successfully updated in Neo4j Desktop!")
    except Exception as e:
        print(f"[-] Connection Failed: {e}")
        print("TIP: Make sure the 'Start' button is clicked in Neo4j Desktop.")
        sys.exit(1)
    finally:
        driver.close()

if __name__ == "__main__":
    run_import()
