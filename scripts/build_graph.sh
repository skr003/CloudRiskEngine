#!/bin/bash
set -euo pipefail

NEO4J_URI="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASS="${NEO4J_PASSWORD}" # Set this env var in Jenkins
ASSIGN_FILE="output/role_assignments.json"

echo "[*] [Module 2] Building Graph in Neo4j..."

# Clear DB (Optional - be careful!)
echo "MATCH (n) DETACH DELETE n;" | cypher-shell -u $NEO4J_USER -p $NEO4J_PASS --address $NEO4J_URI

# Use jq to stream Cypher MERGE commands
# Note: This uses the optimized batch approach
cat $ASSIGN_FILE | jq -r '
  to_entries | .[] | 
  (if (.key % 1000 == 0) then ":commit\n:begin\n" else "" end) +
  "MERGE (p:Principal {id:\"" + .value.principalId + "\", type:\"" + .value.principalType + "\"}) 
   MERGE (r:Role {name:\"" + .value.roleDefinitionName + "\"}) 
   MERGE (p)-[:ASSIGNED {scope:\"" + .value.scope + "\"}]->(r);"
' > import_graph.cypher

# Run Import
cat import_graph.cypher | cypher-shell -u $NEO4J_USER -p $NEO4J_PASS --address $NEO4J_URI

echo "[+] Graph construction complete."
