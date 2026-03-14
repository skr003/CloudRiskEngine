import json
from neo4j import GraphDatabase

URI = "bolt+ssc://a7c4fec6.databases.neo4j.io" 
USER = "neo4j"
PASS = "pUTM7SqI9HE6H8awExoZK2PKEHznG2sIMFYEaibOwY8" 
CYPHER_FILE = "import.cypher"

def update_identities():
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    
    # Files we generated in Stage 1
    files = {
        "Users": "output/ad_users.json",
        "SPS": "output/ad_sps.json",
        "Groups": "output/ad_groups.json"
    }

    with driver.session() as session:
        for category, file_path in files.items():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    print(f"[*] Merging {len(data)} {category} into Neo4j...")
                    
                    # This Cypher query finds the node by ID and adds the display name
                    query = """
                    UNWIND $batch AS item
                    MATCH (p:Principal {id: item.id})
                    SET p.displayName = item.displayName, 
                        p.principalName = item.principalName
                    """
                    session.run(query, batch=data)
            except Exception as e:
                print(f"[!] Skipping {category}: {e}")

    driver.close()

if __name__ == "__main__":
    update_identities()
