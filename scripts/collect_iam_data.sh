#!/bin/bash
set -euo pipefail

OUTPUT_DIR="output"
mkdir -p $OUTPUT_DIR

echo "[*] [Module 1] Collecting Azure IAM Data..."

# 1. Get Role Definitions (needed for permissions)
az role definition list --output json > $OUTPUT_DIR/role_definitions.json

# 2. Get Role Assignments (who has what)
az role assignment list --all --output json > $OUTPUT_DIR/role_assignments.json

# 3. Get Activity Logs (optional context)
az monitor activity-log list --max-events 500 --output json > $OUTPUT_DIR/activity_logs.json

echo "[+] Data collection complete."
