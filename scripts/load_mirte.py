import sys
import os
from neo4j import GraphDatabase

# Using the exact credentials that worked for your Aura instance
URI = "bolt+ssc://a7c4fec6.databases.neo4j.io" 
USER = "neo4j"
PASS = "PASTE_YOUR_NEW_PASSWORD_HERE" 

# Point this to whatever file your import_mitre.sh generates
CYPHER_FILE = "mitre.cypher" 

def run_mitre_import():
    if not os.path.exists(CYPHER_FILE):
        print(f"[-] Error: {CYPHER_FILE} not found.")
        sys.exit(1)

    print(f"[*] Pushing MITRE data to Aura: {URI}...")
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    
    try:
        with driver.session() as session:
            with open(CYPHER_FILE, 'r') as f:
                queries = [q.strip() for q in f.read().split(';') if q.strip()]
            
            print(f"[*] Executing {len(queries)} MITRE queries...")
            with session.begin_transaction() as tx:
                for query in queries:
                    tx.run(query)
                
            print("[+] Success! MITRE ATT&CK nodes added to the Cloud Risk Engine.")
            
    except Exception as e:
        print(f"[-] FATAL ERROR: {e}")
        sys.exit(1)
    finally:
        driver.close()

if __name__ == "__main__":
    run_mitre_import()
