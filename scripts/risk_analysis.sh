#!/bin/bash
set -euo pipefail

NEO4J_URI="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASS="Admin@123$%^"

echo "[*] Detecting Privilege Escalation Paths..."
cypher-shell -u $NEO4J_USER -p $NEO4J_PASS --address $NEO4J_URI "
MATCH path = (p:Principal)-[:ASSIGNED*1..3]->(r:Role)
WHERE r.name CONTAINS 'Owner' OR r.name CONTAINS 'Contributor'
RETURN p.id, nodes(path), relationships(path)
" > output/escalation_paths.txt

echo "[*] Risk scoring: counting high-privilege assignments..."
cypher-shell -u $NEO4J_USER -p $NEO4J_PASS --address $NEO4J_URI "
MATCH (p:Principal)-[:ASSIGNED]->(r:Role)
WHERE r.name =~ '(?i).*owner.*|.*contributor.*'
RETURN p.id, r.name, COUNT(*) as risk_score
" > output/risk_scores.csv
