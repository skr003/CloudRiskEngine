#!/bin/bash
set -euo pipefail

# Configuration
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASS="Admin@123$%^" 

INPUT_MAPPING="output/mitre_mapping.json"
OUTPUT_RESULT="output/mitre_mapping_with_name.json"

# --- Part 1: Import TTPs into Neo4j (Using cypher-shell) ---
if [ ! -f "$INPUT_MAPPING" ]; then
    echo "Error: $INPUT_MAPPING not found. Run map_mitre.py first."
    exit 1
fi

echo "[*] [Module 3] Importing TTP Nodes..."

# 1. Generate Cypher for Import
cat $INPUT_MAPPING | jq -r '
  .[] | 
  "MERGE (r:Role {name:\"" + .role + "\"}) " +
  "MERGE (t:TTP {id:\"" + .ttp + "\"}) " +
  "MERGE (r)-[:ALLOWS_TECHNIQUE {action:\"" + .action + "\"}]->(t);"
' > import_ttp.cypher

# 2. Run Import Transaction
echo ":begin" > transaction.cypher
cat import_ttp.cypher >> transaction.cypher
echo ":commit" >> transaction.cypher

# We use standard cypher-shell here (no JSON format needed for import)
cat transaction.cypher | cypher-shell -u $NEO4J_USER -p $NEO4J_PASS --address $NEO4J_URI

# Cleanup temp files
rm import_ttp.cypher transaction.cypher
echo "[+] Import complete."

# --- Part 2: Export Graph Analysis (FIXED) ---
echo "[*] [Module 3] Generating Analysis Report ($OUTPUT_RESULT)..."

# FIX: Use Python instead of cypher-shell --format json
# This avoids the "invalid choice: json" error on older clients.
python3 -c "
import os
import json
from neo4j import GraphDatabase

uri = os.environ.get('NEO4J_URI')
user = os.environ.get('NEO4J_USER')
password = os.environ.get('NEO4J_PASS')
output_file = '$OUTPUT_RESULT'

query = \"\"\"
MATCH (u:Principal)-[:ASSIGNED]->(r:Role)-[rel:ALLOWS_TECHNIQUE]->(t:TTP)
RETURN 
    u.id AS User, 
    r.name AS Role, 
    rel.action AS DangerousPermission, 
    t.id AS MitreID
ORDER BY u.id
\"\"\"

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        result = session.run(query)
        # Convert Neo4j records to a clean list of dictionaries
        data = [dict(record) for record in result]

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f\"[+] Successfully exported {len(data)} records to {output_file}\")
    driver.close()

except Exception as e:
    print(f\"[!] Error during export: {e}\")
    exit(1)
"

echo "[+] Analysis saved to $OUTPUT_RESULT"
