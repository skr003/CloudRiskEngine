import sys
import os
from neo4j import GraphDatabase

# UPDATE THESE from your Aura downloaded credentials file
URI = "neo4j+s://your-unique-id.databases.neo4j.io" 
USER = "neo4j"
PASS = "your-generated-aura-password" 
CYPHER_FILE = "import.cypher"

def run_import():
    if not os.path.exists(CYPHER_FILE):
        print(f"[-] Error: {CYPHER_FILE} not found.")
        sys.exit(1)

    # Aura requires the +s protocol for security
    print(f"[*] Connecting to Neo4j Aura...")
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    
    try:
        # In Aura Free, the database name is always 'neo4j'
        with driver.session(database="neo4j") as session:
            print("[*] Wiping old data from Aura...")
            session.run("MATCH (n) DETACH DELETE n")

            with open(CYPHER_FILE, 'r') as f:
                # Filter out :begin/:commit lines
                queries = [q.strip() for q in f.read().split(';') if q.strip() and not q.startswith(':')]
            
            print(f"[*] Executing {len(queries)} queries on Cloud instance...")
            with session.begin_transaction() as tx:
                for query in queries:
                    tx.run(query)
                
            print("[+] Success! Aura graph updated.")
    except Exception as e:
        print(f"[-] Aura Connection Failed: {e}")
        sys.exit(1)
    finally:
        driver.close()

if __name__ == "__main__":
    run_import()
