import sys
import os
from neo4j import GraphDatabase

# --- AURA DB CONNECTION SETTINGS ---
# Using bolt+ssc:// to bypass local Windows certificate/routing issues
URI = "bolt+ssc://a7c4fec6.databases.neo4j.io" 
USER = "neo4j"
PASS = "PASTE_YOUR_NEW_PASSWORD_HERE" # Update this with your actual Aura instance password

# This must perfectly match the output file from import_mitre.sh
CYPHER_FILE = "mitre.cypher" 

def run_mitre_import():
    if not os.path.exists(CYPHER_FILE):
        print(f"[-] Error: {CYPHER_FILE} not found. Did the Bash script run successfully?")
        sys.exit(1)

    print(f"[*] Pushing MITRE data to AuraDB: {URI}...")
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    
    try:
        # Verify connection before attempting to execute
        driver.verify_connectivity()
        
        with driver.session() as session:
            with open(CYPHER_FILE, 'r') as f:
                # Split the file by semicolons to execute individual queries
                queries = [q.strip() for q in f.read().split(';') if q.strip()]
            
            print(f"[*] Executing {len(queries)} MITRE node queries...")
            
            with session.begin_transaction() as tx:
                for query in queries:
                    tx.run(query)
                
            print("[+] Success! MITRE ATT&CK nodes safely added to the Cloud Risk Engine graph.")
            
    except Exception as e:
        print(f"[-] FATAL ERROR: {e}")
        sys.exit(1)
    finally:
        driver.close()

if __name__ == "__main__":
    run_mitre_import()
