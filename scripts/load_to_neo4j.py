import sys
import os
from neo4j import GraphDatabase

# 1. HARDCODE YOUR CREDENTIALS HERE
# Using bolt+ssc bypasses both routing errors and Windows SSL certificate issues
URI = "bolt+ssc://a7c4fec6.databases.neo4j.io" 
USER = "neo4j"
PASS = "pUTM7SqI9HE6H8awExoZK2PKEHznG2sIMFYEaibOwY8" 

CYPHER_FILE = "output/mitre_mapping_with_name.json"

def run_import():
    if not os.path.exists(CYPHER_FILE):
        print(f"[-] Error: {CYPHER_FILE} not found.")
        sys.exit(1)

    print(f"[*] Connecting securely to new Aura instance: {URI}...")
    
    # Initialize the driver
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    
    try:
        driver.verify_connectivity()
        print("[+] Authentication Successful!")
        
        # Open session without naming the database (required for Aura)
        with driver.session() as session:
            print("[*] Wiping old data...")
            session.run("MATCH (n) DETACH DELETE n")

            with open(CYPHER_FILE, 'r') as f:
                queries = [q.strip() for q in f.read().split(';') if q.strip()]
            
            print(f"[*] Executing {len(queries)} queries...")
            with session.begin_transaction() as tx:
                for query in queries:
                    tx.run(query)
                
            print("[+] Success! Cloud risk graph updated on AuraDB.")
            
    except Exception as e:
        print(f"[-] FATAL ERROR: {e}")
        sys.exit(1)
    finally:
        driver.close()

if __name__ == "__main__":
    run_import()
