#!/bin/bash
set -euo pipefail

NEO4J_URI="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASS="test123"

ROLE_FILE="output/role_definitions.json"
ASSIGN_FILE="output/role_assignments.json"

echo "[*] Importing Roles into Neo4j..."
cat $ROLE_FILE | jq -c '.[]' | while read role; do
  name=$(echo $role | jq -r '.roleName')
  azs=$(echo $role | jq -r '.assignableScopes[]?')
  cypher="MERGE (r:Role {name:'$name'})"
  echo $cypher | cypher-shell -u $NEO4J_USER -p $NEO4J_PASS --address $NEO4J_URI
done

echo "[*] Importing Role Assignments..."
cat $ASSIGN_FILE | jq -c '.[]' | while read asg; do
  principal=$(echo $asg | jq -r '.principalId')
  role=$(echo $asg | jq -r '.roleDefinitionName')
  cypher="MERGE (p:Principal {id:'$principal'}) MERGE (r:Role {name:'$role'}) MERGE (p)-[:ASSIGNED]->(r)"
  echo $cypher | cypher-shell -u $NEO4J_USER -p $NEO4J_PASS --address $NEO4J_URI
done
