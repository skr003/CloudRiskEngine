#!/bin/bash
set -euo pipefail

OUTPUT_DIR="output"
mkdir -p $OUTPUT_DIR

# Optimization 1: Skip 'az role definition list'. 
# The assignment list contains the Role Name needed for the graph.
# Downloading definitions is only necessary if you need to map specific permissions (Actions/NotActions).

echo "[*] Collecting Azure IAM Role Definitions..."
az role definition list --output json > $OUTPUT_DIR/role_definitions.json

echo "[*] Collecting Role Assignments (All Users)..."
# Optimization 2: Use --all to ensure we get everything, but output is standard
az role assignment list --all --output json > $OUTPUT_DIR/role_assignments.json

echo "[*] Collecting Activity Logs (last 30 days)..."
# Keep this as is, but ensure we don't fetch too much if the subscription is huge.
# You might want to filter by 'eventTimestamp' if this is too slow.
az monitor activity-log list --max-events 1000 --output json > $OUTPUT_DIR/activity_logs.json

echo "[*] Data collection complete."
