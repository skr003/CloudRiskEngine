import sys
import os
import dotenv
from neo4j import GraphDatabase

# 1. UPDATE THIS LINE with the exact name of your NEW downloaded .txt file
ENV_FILE = "scripts/Neo4j-a7c4fec6-Created-2026-03-14.txt"
CYPHER_FILE = "import.cypher"

def run_import():
    # Load the new credentials
    if not dotenv.load_dotenv(ENV_FILE):
        print(f"[-] Error: Could not load Aura environment file: {ENV_FILE}")
        sys.exit(1)

    # Automatically bypass routing using the bolt+s:// trick
    raw_uri = os.getenv("NEO4J_URI")
    URI = raw_uri.replace("neo4j+s://", "bolt+s://") 
    AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

    if not os.path.exists(CYPHER_FILE):
        print(f"[-] Error: {CYPHER_FILE} not found.")
        sys.exit(1)

    print(f"[*] Connecting directly via Bolt to new instance: {URI}...")
    
    driver = GraphDatabase.driver(URI, auth=AUTH)
    
    try:
        driver.verify_connectivity()
        print("[+] Connection established successfully.")
        
        # Use the default session to avoid 'DatabaseNotFound' errors
        with driver.session() as session:
            print("[*] Wiping old data from Aura...")
            session.run("MATCH (n) DETACH DELETE n")

            with open(CYPHER_FILE, 'r') as f:
                queries = [q.strip() for q in f.read().split(';') if q.strip()]
            
            print(f"[*] Executing {len(queries)} queries...")
            with session.begin_transaction() as tx:
                for query in queries:
                    tx.run(query)
                
            print("[+] Success! Cloud risk graph updated on AuraDB Professional.")
            
    except Exception as e:
        print(f"[-] FATAL ERROR: {e}")
        sys.exit(1)
    finally:
        driver.close()

if __name__ == "__main__":
    run_import()
