#!/bin/bash
set -euo pipefail

# Require a target user (Email or Object ID)
if [ -z "${1:-}" ]; then
    echo "Usage: $0 sudharshankr003@gmail.com"
    exit 1
fi

TARGET_USER="$1"
OUTPUT_DIR="output"
mkdir -p $OUTPUT_DIR

echo "[*] Collecting data for: $TARGET_USER"

# 1. Collect ONLY assignments for this specific user
# Optimization: Uses --assignee to filter at the API level
echo "[*] Collecting Role Assignments..."
az role assignment list \
    --assignee "$TARGET_USER" \
    --include-inherited \
    --output json > $OUTPUT_DIR/role_assignments.json

# 2. Collect Activity Logs ONLY for this caller
# Optimization: Uses --caller to avoid fetching global logs
echo "[*] Collecting Activity Logs (last 30 days)..."
az monitor activity-log list \
    --caller "$TARGET_USER" \
    --max-events 1000 \
    --output json > $OUTPUT_DIR/activity_logs.json

# Note: We skip downloading 'role_definitions.json' entirely.
# The assignment list contains the Role Names we need for the graph.
