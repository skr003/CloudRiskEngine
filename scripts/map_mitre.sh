#!/bin/bash
set -euo pipefail

ROLE_FILE="output/role_definitions.json"
MITRE_MAP="config/mitre_mapping.json"
OUTPUT_FILE="output/mitre_mapping.json"

# 1. Pre-flight Checks
if [ ! -f "$ROLE_FILE" ]; then
    echo "Error: $ROLE_FILE not found. Run 'az role definition list > $ROLE_FILE' first."
    exit 1
fi

if [ ! -f "$MITRE_MAP" ]; then
    echo "Error: $MITRE_MAP not found. Please create the mapping file in config/."
    exit 1
fi

# Clear previous output
> $OUTPUT_FILE

echo "[*] Mapping Azure Actions to MITRE TTPs..."

# 2. Process Roles
# We use a temporary file to handle the loop safely avoiding pipe subshells
jq -c '.[]' $ROLE_FILE | while read role; do
  
  # Extract Role Name
  name=$(echo $role | jq -r '.roleName')
  
  # Extract Actions (using -r to get raw strings without quotes)
  # We check both 'actions' and 'dataActions'
  actions=$(echo $role | jq -r '.permissions[] | (.actions[]?, .dataActions[]?)')

  for act in $actions; do
    # 3. Lookup TTP
    # We strip the wildcard '/*' if present to match the generic TTPs if needed
    clean_act="${act%/*}" 

    # Check exact match first
    ttp=$(jq -r --arg a "$act" '.[$a] // empty' $MITRE_MAP)
    
    # If no exact match, try matching the wildcard version (optional logic)
    if [ -z "$ttp" ]; then
        ttp=$(jq -r --arg a "$clean_act" '.[$a] // empty' $MITRE_MAP)
    fi

    if [ ! -z "$ttp" ]; then
      echo "MATCH: $name uses $act -> $ttp"
      # Append to JSON file (NDJSON format for easier processing, or wrap in array later)
      echo "{\"role\":\"$name\", \"action\":\"$act\", \"ttp\":\"$ttp\"}" >> $OUTPUT_FILE
    fi
  done
done

echo "[*] Done. Results saved to $OUTPUT_FILE"
