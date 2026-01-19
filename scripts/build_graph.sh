#!/bin/bash
set -euo pipefail

NEO4J_URI="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASS="Admin@123$%^"  # Ideally, switch this to an env variable like $NEO4J_PASSWORD

ASSIGN_FILE="output/role_assignments.json"

# Check if file exists and has data
if [ ! -s "$ASSIGN_FILE" ] || [ "$(jq 'length' $ASSIGN_FILE)" -eq 0 ]; then
    echo "Error: $ASSIGN_FILE is empty or missing. Did the user have any assignments?"
    exit 1
fi

echo "[*] Importing Role Assignments for target user..."

# Optimization:
# 1. We removed the loop over 'role_definitions.json'. 
#    We don't need to import 5000+ unused roles.
# 2. We MERGE the Role node inside this loop. 
#    This ensures we only create nodes for roles the user actually HAS.

cat $ASSIGN_FILE | jq -c '.[]' | while read asg; do
  # Extract data
  principal=$(echo $asg | jq -r '.principalId')
  roleName=$(echo $asg | jq -r '.roleDefinitionName')
  scope=$(echo $asg | jq -r '.scope')

  # Construct Query
  # - Creates the Principal node (User)
  # - Creates the Role node (only if it doesn't exist)
  # - Links them with ASSIGNED {scope: ...}
  cypher="
    MERGE (p:Principal {id:'$principal'})
    MERGE (r:Role {name:'$roleName'})
    MERGE (p)-[:ASSIGNED {scope:'$scope'}]->(r)
  "

  # Execute
  echo "$cypher" | cypher-shell -u $NEO4J_USER -p $NEO4J_PASS --address $NEO4J_URI
done

echo "[*] Import complete."
