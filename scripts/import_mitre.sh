#!/bin/bash
set -euo pipefail

NEO4J_URI="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASS="${NEO4J_PASSWORD}"

echo "[*] [Module 3] Importing TTP Nodes..."
cat output/mitre_matches.json | jq -r '
  .[] | 
  "MERGE (r:Role {name:\"" + .role + "\"}) " +
  "MERGE (t:TTP {id:\"" + .ttp + "\"}) " +
  "MERGE (r)-[:ALLOWS_TECHNIQUE {action:\"" + .action + "\"}]->(t);"
' | cypher-shell -u $NEO4J_USER -p $NEO4J_PASS --address $NEO4J_URI
