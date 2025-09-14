# -------------------
# Build final payload (big file + flattened per-entity files)
# -------------------
echo "📝 Building final payload -> $OUTFILE"
jq -n \
  --arg collectedAt "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
  --slurpfile roleAssignments "$ENRICHED_FILE" \
  --slurpfile roleDefinitions "$ROLEDEFS_FILE" \
  --slurpfile users "$USERS_FILE" \
  --slurpfile groups "$GROUPS_FILE" \
  --slurpfile sps "$SPS_FILE" \
  --slurpfile activityLogs "$OUTDIR/activityLogs.json" \
  '{
    collectedAt: $collectedAt,
    roleAssignments: $roleAssignments[0],
    roleDefinitions: $roleDefinitions[0],
    users: $users[0],
    groups: $groups[0],
    servicePrincipals: $sps[0],
    activityLogs: $activityLogs[0]
  }' > "$OUTFILE"

# -------------------
# Also export flat files for Grafana
# -------------------
cp "$USERS_FILE"            "$OUTDIR/azure_users.json"
cp "$GROUPS_FILE"           "$OUTDIR/azure_groups.json"
cp "$SPS_FILE"              "$OUTDIR/azure_sps.json"
cp "$ENRICHED_FILE"         "$OUTDIR/azure_role_assignments.json"
cp "$ROLEDEFS_FILE"         "$OUTDIR/azure_role_definitions.json"
cp "$OUTDIR/activityLogs.json" "$OUTDIR/azure_activity_logs.json"

# -------------------
# Final sanity counts
# -------------------
echo "✅ Collected -> $OUTFILE (and flat Grafana files)"
echo "   Users:    $(jq 'length' "$USERS_FILE")"
echo "   Groups:   $(jq 'length' "$GROUPS_FILE")"
echo "   SPs:      $(jq 'length' "$SPS_FILE")"
echo "   Assigns:  $(jq 'length' "$ENRICHED_FILE")"
echo "   RoleDefs: $(jq 'length' "$ROLEDEFS_FILE")"
echo "   Activities: $(jq 'length' "$OUTDIR/activityLogs.json")"
