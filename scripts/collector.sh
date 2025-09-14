#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="output"
OUTPUT_FILE="$OUTPUT_DIR/azure_data.json"

mkdir -p "$OUTPUT_DIR"

# Run az and capture JSON
run() {
  local cmd=("$@")
  "${cmd[@]}"
}

collect_role_assignments() {
  run az role assignment list --all -o json
}

collect_role_definitions() {
  run az role definition list -o json
}

collect_activity_logs() {
  local days="${1:-7}"
  local end start timespan
  end=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  start=$(date -u -d "$days days ago" +"%Y-%m-%dT%H:%M:%SZ")
  timespan="$start/$end"
  run az monitor activity-log list --timespan "$timespan" -o json
}

resolve_principal_name() {
  local pid="$1"
  local ptype="$2"
  local out

  case "$ptype" in
    User)
      out=$(az ad user show --id "$pid" -o json 2>/dev/null || true)
      ;;
    ServicePrincipal)
      out=$(az ad sp show --id "$pid" -o json 2>/dev/null || true)
      ;;
    Group)
      out=$(az ad group show --group "$pid" -o json 2>/dev/null || true)
      ;;
    *)
      out=""
      ;;
  esac

  if [[ -n "$out" ]]; then
    echo "$out" | jq -r '.displayName // .appDisplayName // .userPrincipalName // empty'
  else
    echo ""
  fi
}

enrich_assignments() {
  local assignments="$1"
  echo "$assignments" | jq -c '.[]' | while read -r a; do
    pid=$(echo "$a" | jq -r '.principalId')
    ptype=$(echo "$a" | jq -r '.principalType')

    name=$(resolve_principal_name "$pid" "$ptype")
    if [[ -z "$name" || "$name" == "null" ]]; then
      name=$(echo "$a" | jq -r '.principalDisplayName // .principalName // .principalId')
    fi

    echo "$a" | jq --arg name "$name" '. + {resourceName: $name}'
  done | jq -s '.'
}

main() {
  echo "⏳ Collecting data from Azure..."

  assignments=$(collect_role_assignments)
  role_defs=$(collect_role_definitions)
  logs=$(collect_activity_logs 7)

  enriched=$(enrich_assignments "$assignments")

  now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  jq -n \
    --arg collectedAt "$now" \
    --argjson roleAssignments "$enriched" \
    --argjson roleDefinitions "$role_defs" \
    --argjson activityLogs "$logs" \
    '{
      collectedAt: $collectedAt,
      roleAssignments: $roleAssignments,
      roleDefinitions: $roleDefinitions,
      activityLogs: $activityLogs
    }' > "$OUTPUT_FILE"

  echo "✅ Collected -> $OUTPUT_FILE (resourceName = displayName)"
}

main "$@"
