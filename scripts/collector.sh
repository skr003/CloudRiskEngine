#!/usr/bin/env bash
set -euo pipefail

OUTDIR="output"
OUTFILE="$OUTDIR/azure_data.json"
mkdir -p "$OUTDIR"

# -------------------
# Helper to run AZ CLI safely
# -------------------
run() {
  az "$@" -o json 2>/dev/null || echo "[]"
}

# -------------------
# Collect raw data
# -------------------
echo "📥 Collecting role assignments..."
ASSIGNMENTS=$(run role assignment list --all)

echo "📥 Collecting role definitions..."
ROLE_DEFS=$(run role definition list)

echo "📥 Collecting activity logs..."
END=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
START=$(date -u -d "-7 days" +"%Y-%m-%dT%H:%M:%SZ")
LOGS=$(az monitor activity-log list \
  --start-time "$START" --end-time "$END" -o json 2>/dev/null || echo "[]")

# -------------------
# Collect principals (via MS Graph where needed)
# -------------------
echo "📥 Collecting users..."
USERS=$(run ad user list)

echo "📥 Collecting service principals..."
SPS=$(run ad sp list)

echo "📥 Collecting groups (via MS Graph)..."
GROUPS=$(az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/groups?\$top=999" \
  --query "value[].{id:id, displayName:displayName}" \
  -o json 2>/dev/null || echo "[]")

# -------------------
# Enrich assignments with principal display names
# -------------------
echo "✨ Enriching assignments..."
ENRICHED=$(jq -n \
  --argjson assignments "$ASSIGNMENTS" \
  --argjson users "$USERS" \
  --argjson sps "$SPS" \
  --argjson groups "$GROUPS" '
  def lookup(pid; arr):
    (arr[] | select(.id == pid) | .displayName // .appDisplayName // .userPrincipalName) // null;

  [$assignments[] | . + {
    resourceName:
      (lookup(.principalId; $users)
       // lookup(.principalId; $sps)
       // lookup(.principalId; $groups)
       // .principalDisplayName
       // .principalName
       // .principalId)
  }]
')

# -------------------
# Build final payload
# -------------------
echo "📝 Building output..."
jq -n \
  --arg collectedAt "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
  --argjson roleAssignments "$ENRICHED" \
  --argjson roleDefinitions "$ROLE_DEFS" \
  --argjson activityLogs "$LOGS" \
  '{
    collectedAt: $collectedAt,
    roleAssignments: $roleAssignments,
    roleDefinitions: $roleDefinitions,
    activityLogs: $activityLogs
  }' > "$OUTFILE"

echo "✅ Collected -> $OUTFILE"
