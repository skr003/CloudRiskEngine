#!/bin/bash
# scripts/build_graph.sh

ASSIGN_FILE="output/role_assignments.json"
CYPHER_FILE="import.cypher"

# 1. Validation: Ensure the data source exists
if [ ! -s "$ASSIGN_FILE" ]; then
    echo "Error: $ASSIGN_FILE is missing or empty."
    exit 1
fi

echo "[*] Generating Cypher queries from $ASSIGN_FILE..."

# 2. Transform JSON to Cypher MERGE statements
# MERGE ensures we don't create duplicate nodes if the script runs twice.
"C:\Program Files\jq\jq.exe" -r '.[] | "MERGE (p:Principal {id:\"\(.principalId)\"}) MERGE (r:Role {name:\"\(.roleDefinitionName)\"}) MERGE (p)-[:ASSIGNED {scope:\"\(.scope)\"}]->(r);"' "$ASSIGN_FILE" > "$CYPHER_FILE"

echo "[*] Cypher file generated: $CYPHER_FILE"
