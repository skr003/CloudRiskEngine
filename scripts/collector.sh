#!/usr/bin/env bash
set -euo pipefail

OUTDIR="output"
OUTFILE="$OUTDIR/azure_data.json"
mkdir -p "$OUTDIR"

# -------------------
# Helper: collect all pages from Graph
# -------------------
graph_collect_all() {
  local url=$1
  local results="[]"

  while [[ -n "$url" && "$url" != "null" ]]; do
    echo "➡️  Fetching $url"
    page=$(az rest --method GET --url "$url" -o json 2>/dev/null || echo "{}")
    values=$(echo "$page" | jq '.value // []')
    results=$(jq -n --argjson a "$results" --argjson b "$values" '$a + $b')
    url=$(echo "$page" | jq -r '."@odata.nextLink" // empty')
  done

  echo "$results"
}

# -------------------
# Collect raw data
# -------------------
echo "📥 Collecting role assignments..."
ASSIGNMENTS=$(az role assignment list --all -o json 2>/dev/null || echo "[]")

echo "📥 Collecting role definitions..."
ROLE_DEFS=$(az role definition list -o json 2>/dev/null || echo "[]")

echo "📥 Collecting activity logs..."
END=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
START=$(date -u -d "-7 days" +"%Y-%m-%dT%H:%M:%SZ")
LOGS=$(az monitor activity-log list \
  --start-time "$START" --end-time "$END" -o json 2>/dev/null || echo "[]")

# -------------------
# Collect principals via Graph API
# -------------------
echo "📥 Collecting users (Graph API)..."
USERS=$(graph_collect_all "https://graph.microsoft.com/v1.0/users?\$select=id,displayName,userPrincipalName")

echo "📥 Collecting service principals (Graph API)..."
SPS=$(graph_collect_all "https://graph.microsoft.com/v1.0/servicePrincipals?\$select=id,appId,displayName,appDisplayName")

echo "📥 Collecting groups (Graph API)..."
GROUPS=$(graph_collect_all "https://graph.microsoft.com/v1.0/groups?\$select=id,displayName")

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
