#!/bin/bash
set -euo pipefail

ASSIGN_FILE="output/role_assignments.json"
CYPHER_FILE="import.cypher"

# 1. Validation
if [ ! -s "$ASSIGN_FILE" ]; then
    echo "Error: $ASSIGN_FILE is missing or empty."
    exit 1
fi

echo "[*] Generating Cypher queries..."

# 2. Convert JSON to Cypher strings
# Use double quotes for the shell but single quotes for JQ interpolation to avoid 'syntax error'
"C:\Program Files\jq\jq.exe" -r '.[] | "MERGE (p:Principal {id:\"\(.principalId)\"}) MERGE (r:Role {name:\"\(.roleDefinitionName)\"}) MERGE (p)-[:ASSIGNED {scope:\"\(.scope)\"}]->(r);"' "$ASSIGN_FILE" > "$CYPHER_FILE"

echo "[*] Import file generated: $CYPHER_FILE"
