import sys
import os
from neo4j import GraphDatabase

# Config
URI = "bolt://localhost:7687"
USER = "neo4j"
PASS = "Admin@123$%^"
CYPHER_FILE = "import.cypher"

def run_import():
    if not os.path.exists(CYPHER_FILE):
        print(f"Error: {CYPHER_FILE} not found.")
        sys.exit(1)

    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    try:
        with driver.session() as session:
            with open(CYPHER_FILE, 'r') as f:
                # Read file, ignore transaction markers (:begin/:commit), and split by semicolon
                content = f.read()
                queries = [q.strip() for q in content.split(';') if q.strip() and not q.startswith(':')]
                
                print(f"[*] Found {len(queries)} queries. Starting import...")
                
                # Execute in a single transaction for speed
                with session.begin_transaction() as tx:
                    for query in queries:
                        tx.run(query)
                
        print("[+] Import successful!")
    except Exception as e:
        print(f"[-] Error during import: {e}")
        sys.exit(1)
    finally:
        driver.close()

if __name__ == "__main__":
    run_import()
