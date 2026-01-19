#!/bin/bash
set -euo pipefail

OUTPUT_DIR="output"
mkdir -p $OUTPUT_DIR

echo "[*] Collecting Azure IAM Role Definitions..."
az role definition list --output json > $OUTPUT_DIR/role_definitions.json

echo "[*] Collecting Role Assignments..."
az role assignment list --all --output json > $OUTPUT_DIR/role_assignments.json

echo "[*] Collecting Activity Logs (last 30 days)..."
az monitor activity-log list --max-events 10 --output json > $OUTPUT_DIR/activity_logs.json
