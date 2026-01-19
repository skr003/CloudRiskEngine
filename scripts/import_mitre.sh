#!/bin/bash
set -euo pipefail

NEO4J_URI="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASS="Admin@123$%^"
MAPPING_FILE="output/mitre_mapping_with_name.json"

if [ ! -f "$MAPPING_FILE" ]; then
    echo "Error: $MAPPING_FILE not found. Run map_mitre.py first."
    exit 1
fi

echo "[*] Importing MITRE TTPs into Neo4j..."

# We use jq to prepare the Cypher query.
# This creates a TTP node and links it to the Role.
cat $MAPPING_FILE | jq -r '
  .[] | 
  "MERGE (r:Role {name:\"" + .role + "\"}) " +
  "MERGE (t:TTP {id:\"" + .ttp + "\"}) " +
  "MERGE (r)-[:ALLOWS_TECHNIQUE {action:\"" + .action + "\"}]->(t);"
' > import_ttp.cypher

# Use a single transaction for speed
echo ":begin" > transaction.cypher
cat import_ttp.cypher >> transaction.cypher
echo ":commit" >> transaction.cypher

# Run the import
cat transaction.cypher | cypher-shell -u $NEO4J_USER -p $NEO4J_PASS --address $NEO4J_URI

# Cleanup
rm import_ttp.cypher transaction.cypher
echo "[*] Import complete."
