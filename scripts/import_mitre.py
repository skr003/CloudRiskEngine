import json
from neo4j import GraphDatabase

# Aura Connection
URI = "bolt+ssc://a7c4fec6.databases.neo4j.io" 
USER = "neo4j"
PASS = "pUTM7SqI9HE6H8awExoZK2PKEHznG2sIMFYEaibOwY8"

def force_import_mitre():
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    # Path to your mapping file
    file_path = "mitre_mapping.json" 
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        with driver.session() as session:
            print(f"[*] Importing {len(data)} techniques...")
            query = """
            UNWIND $batch AS tech
            MERGE (t:Technique {id: tech.id})
            SET t.name = tech.name, 
                t.tactic = tech.tactic
            """
            session.run(query, batch=data)
            print("[+] MITRE Import Successful.")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    force_import_mitre()
