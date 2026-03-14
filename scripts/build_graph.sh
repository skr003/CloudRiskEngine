#!/bin/bash
set -euo pipefail

NEO4J_URI="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASS="Admin@123$%^"

ASSIGN_FILE="output/role_assignments.json"

# Check if file exists
if [ ! -s "$ASSIGN_FILE" ]; then
    echo "Error: $ASSIGN_FILE is missing or empty."
    exit 1
fi

echo "[*] Generating Cypher queries..."

# Optimization 3: Create a temporary file with all Cypher commands
# We use jq to transform the JSON directly into Cypher strings.
# This avoids the slow bash 'while read' loop entirely.

CYPHER_FILE="import.cypher"

# 1. Start Transaction
echo ":begin" > $CYPHER_FILE

# 2. Convert JSON objects to Cypher MERGE statements

# Define the jq filter in a variable to keep the cat command clean
FILTER_QUERY=$(cat <<'EOF'
.[] | 
"MERGE (p:Principal {id:\"" + .principalId + "\"}) 
 MERGE (r:Role {name:\"" + .roleDefinitionName + "\"}) 
 MERGE (p)-[:ASSIGNED {scope:\"" + .scope + "\"}]->(r);"
EOF
)

# Now run jq using that variable
cat "$ASSIGN_FILE" | jq -r "$FILTER_QUERY" >> "$CYPHER_FILE"


# 3. Commit Transaction
echo ":commit" >> $CYPHER_FILE

echo "[*] Importing into Neo4j (Single Connection)..."

# Optimization 4: Pipe the file into a SINGLE cypher-shell instance.
# This is 100x faster than running cypher-shell inside a loop.
cat $CYPHER_FILE | cypher-shell -u $NEO4J_USER -p $NEO4J_PASS --address $NEO4J_URI

# Cleanup
rm $CYPHER_FILE
echo "[*] Import complete."
