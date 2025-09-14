#!/usr/bin/env bash
set -euo pipefail

OUTDIR="output"
OUTFILE="$OUTDIR/azure_data.json"
mkdir -p "$OUTDIR"

USERS_FILE="$OUTDIR/users.json"
SPS_FILE="$OUTDIR/sps.json"
ASSIGNMENTS_FILE="$OUTDIR/assignments.json"
ROLEDEFS_FILE="$OUTDIR/roledefs.json"
ENRICHED_FILE="$OUTDIR/enriched.json"

# -------------------
# Collect raw data
# -------------------
echo "📥 Collecting role assignments..."
az role assignment list --all -o json 2>/dev/null > "$ASSIGNMENTS_FILE" || echo "[]" > "$ASSIGNMENTS_FILE"

echo "📥 Collecting role definitions..."
az role definition list -o json 2>/dev/null > "$ROLEDEFS_FILE" || echo "[]" > "$ROLEDEFS_FILE"

echo "📥 Collecting users (all properties)..."
az ad user list -o json 2>/dev/null > "$USERS_FILE" || echo "[]" > "$USERS_FILE"

echo "📥 Collecting service principals (all properties)..."
az ad sp list -o json 2>/dev/null > "$SPS_FILE" || echo "[]" > "$SPS_FILE"

# Ensure files are valid JSON
for f in "$USERS_FILE" "$SPS_FILE" "$ASSIGNMENTS_FILE" "$ROLEDEFS_FILE"; do
  if ! jq empty "$f" >/dev/null 2>&1; then
    echo "⚠️  $f was invalid, resetting to []"
    echo "[]" > "$f"
  fi
done

# -------------------
# Enrich assignments with displayName/app info
# -------------------
echo "✨ Enriching assignments..."
jq -n \
  --slurpfile assignments "$ASSIGNMENTS_FILE" \
  --slurpfile users "$USERS_FILE" \
  --slurpfile sps "$SPS_FILE" '
  def lookup_user(pid):
    ($users[0][] | select(.id == pid) | .displayName) // null;

  def lookup_sp(pid):
    ($sps[0][] | select(.id == pid) |
      .displayName
      // .appDisplayName
      // .appId) // null;

  [$assignments[0][] | . + {
    resourceName:
      (lookup_user(.principalId)
       // lookup_sp(.principalId)
       // .principalDisplayName
       // .principalName
       // .principalId)
  }]
' > "$ENRICHED_FILE"

# -------------------
# Build final payload
# -------------------
echo "📝 Building output..."
jq -n \
  --arg collectedAt "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
  --slurpfile roleAssignments "$ENRICHED_FILE" \
  --slurpfile roleDefinitions "$ROLEDEFS_FILE" \
  --slurpfile users "$USERS_FILE" \
  --slurpfile sps "$SPS_FILE" \
  '{
    collectedAt: $collectedAt,
    roleAssignments: $roleAssignments[0],
    roleDefinitions: $roleDefinitions[0],
    users: $users[0],
    servicePrincipals: $sps[0]
  }' > "$OUTFILE"

# -------------------
# Sanity check
# -------------------
echo "✅ Collected -> $OUTFILE"
echo "   Users:   $(jq 'length' "$USERS_FILE")"
echo "   SPs:     $(jq 'length' "$SPS_FILE")"
echo "   Assigns: $(jq 'length' "$ENRICHED_FILE")"
