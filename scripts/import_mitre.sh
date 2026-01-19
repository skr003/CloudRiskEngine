#!/bin/bash
set -euo pipefail

NEO4J_URI="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASS="Admin@123$%^"
INPUT_MAPPING="output/mitre_matches.json"
OUTPUT_RESULT="output/mitre_mapping_with_name.json"

# --- Part 1: Import TTPs into Neo4j ---
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

cat transaction.cypher | cypher-shell -u $NEO4J_USER -p $NEO4J_PASS --address $NEO4J_URI

# Cleanup temp files
rm import_ttp.cypher transaction.cypher
echo "[+] Import complete."

# --- Part 2: Export Graph Analysis (The Request) ---
echo "[*] [Module 3] Generating Analysis Report ($OUTPUT_RESULT)..."

# This runs the query you provided and saves the output as a valid JSON Array.
# We use 'jq -s' to combine the JSON Lines output from cypher-shell into a single Array.

QUERY="MATCH (u:Principal)-[:ASSIGNED]->(r:Role)-[rel:ALLOWS_TECHNIQUE]->(t:TTP)
RETURN 
    u.id AS User, 
    r.name AS Role, 
    rel.action AS DangerousPermission, 
    t.id AS MitreID
ORDER BY u.id"

echo "$QUERY" | \
cypher-shell -u $NEO4J_USER -p $NEO4J_PASS --address $NEO4J_URI --format json | \
jq -s '.' > $OUTPUT_RESULT

echo "[+] Analysis saved to $OUTPUT_RESULT"
