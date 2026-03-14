#!/bin/bash
# scripts/build_graph.sh

ASSIGN_FILE="output/role_assignments.json"
CYPHER_FILE="import.cypher"

# Convert JSON to Cypher MERGE statements
"C:\Program Files\jq\jq.exe" -r '.[] | "MERGE (p:Principal {id:\"\(.principalId)\"}) MERGE (r:Role {name:\"\(.roleDefinitionName)\"}) MERGE (p)-[:ASSIGNED {scope:\"\(.scope)\"}]->(r);"' "$ASSIGN_FILE" > "$CYPHER_FILE"

echo "[*] Cypher file generated for Aura."
