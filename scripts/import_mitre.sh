#!/bin/bash
# scripts/import_mitre.sh

INPUT_MAPPING="output/mitre_mapping.json"
CYPHER_FILE="mitre.cypher"

echo "[*] [Stage 4] Parsing MITRE Mapping..."

# 1. Validation check
if [ ! -s "$INPUT_MAPPING" ]; then
    echo "[-] Error: $INPUT_MAPPING is missing or empty. Ensure Stage 2 ran correctly."
    exit 1
fi

# 2. Convert JSON to Cypher using the absolute path to jq
# This extracts the Technique ID, Name, and Tactic and writes them as MERGE commands
"C:\Program Files\jq\jq.exe" -r '.[] | "MERGE (t:Technique {id:\"\(.techniqueId)\"}) SET t.name = \"\(.name)\", t.tactic = \"\(.tactic)\";"' "$INPUT_MAPPING" > "$CYPHER_FILE"

echo "[+] Success: MITRE Cypher queries generated locally in $CYPHER_FILE"
