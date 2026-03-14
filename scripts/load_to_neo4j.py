import sys
import os
from neo4j import GraphDatabase

# --- UPDATE THESE WITH YOUR AURA CREDENTIALS ---
URI = "neo4j+ssc://aa1f8e2f.databases.neo4j.io" 
USER = "neo4j"
PASS = "xUqfRp2e7QFs2xRXw7hGauuDqhyaM2OdOph5R_5zsqI" 
CYPHER_FILE = "import.cypher"

def run_import():
    if not os.path.exists(CYPHER_FILE):
        print(f"[-] Error: {CYPHER_FILE} not found.")
        sys.exit(1)

    print(f"[*] Connecting to Neo4j Aura at {URI}...")
    
    # We use neo4j+s for the encrypted cloud connection
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    
    try:
        # Check connectivity first
        driver.verify_connectivity()
        
        with driver.session(database="neo4j") as session:
            # 1. Clear old graph data for a fresh start
            print("[*] Wiping old data from cloud instance...")
            session.run("MATCH (n) DETACH DELETE n")

            # 2. Read the generated Cypher file
            with open(CYPHER_FILE, 'r') as f:
                queries = [q.strip() for q in f.read().split(';') if q.strip()]
            
            print(f"[*] Executing {len(queries)} queries...")
            
            # 3. Batch execute in a single transaction
            with session.begin_transaction() as tx:
                for query in queries:
                    tx.run(query)
                
            print("[+] Success! Aura graph has been updated.")
            
    except Exception as e:
        print(f"[-] FATAL ERROR: {e}")
        print("TIP: Ensure your URI starts with 'neo4j+s://' and your Aura instance is 'Running'.")
        sys.exit(1)
    finally:
        driver.close()

if __name__ == "__main__":
    run_import()
