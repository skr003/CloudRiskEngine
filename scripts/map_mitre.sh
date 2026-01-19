#!/bin/bash
set -euo pipefail

ROLE_FILE="output/role_definitions.json"
MITRE_MAP="config/mitre_mapping.json" # prebuilt JSON mapping actions -> TTPs

echo "[*] Mapping Azure Actions to MITRE TTPs..."
jq -c '.[]' $ROLE_FILE | while read role; do
  name=$(echo $role | jq -r '.roleName')
  actions=$(echo $role | jq -c '.permissions[].actions[]?')
  for act in $actions; do
    ttp=$(jq -r --arg act $act '.[$act] // empty' $MITRE_MAP)
    if [ ! -z "$ttp" ]; then
      echo "{\"role\":\"$name\", \"action\":$act, \"ttp\":\"$ttp\"}" >> output/mitre_mapping.json
    fi
  done
done
