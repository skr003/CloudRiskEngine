#!/bin/bash
set -euo pipefail

NEO4J_URI="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASS="${NEO4J_PASSWORD:-test123}" # Defaults to test123 if env var not set
ASSIGN_FILE="output/role_assignments.json"
CYPHER_FILE="import_graph.cypher"

echo "[*] [Module 2] Building Graph in Neo4j..."

# Check if input file exists
if [ ! -s "$ASSIGN_FILE" ]; then
    echo "Error: $ASSIGN_FILE is missing or empty."
    exit 1
fi

# 1. Initialize the file with the first transaction start
echo ":begin" > $CYPHER_FILE

# 2. Append Cypher statements
# FIX: checking (.key > 0) ensures we don't commit before we begin on the first row
cat $ASSIGN_FILE | jq -r '
  to_entries | .[] | 
  (if (.key > 0 and .key % 1000 == 0) then ";\n:commit\n:begin\n" else "" end) +
  "MERGE (p:Principal {id:\"" + .value.principalId + "\", type:\"" + (.value.principalType // "User") + "\"}) " +
  "MERGE (r:Role {name:\"" + .value.roleDefinitionName + "\"}) " +
  "MERGE (p)-[:ASSIGNED {scope:\"" + .value.scope + "\"}]->(r);"
' >> $CYPHER_FILE

# 3. Close the final transaction
echo ":commit" >> $CYPHER_FILE

# 4. Execute
echo "[*] Executing Cypher Shell..."
cat $CYPHER_FILE | cypher-shell -u $NEO4J_USER -p $NEO4J_PASS --address $NEO4J_URI

# Cleanup
rm $CYPHER_FILE
echo "[+] Graph construction complete."
