#!/bin/bash
set -euo pipefail

OUTPUT_DIR="output"
mkdir -p $OUTPUT_DIR

echo "[*] Collecting Azure IAM Role Definitions..."
az role definition list --output json > $OUTPUT_DIR/role_definitions.json

echo "[*] Collecting Role Assignments (The Links)..."
az role assignment list --all --output json > $OUTPUT_DIR/role_assignments.json

# =========================================================================
# NEW IDENTITY EXTRACTION MODULE
# This guarantees human-readable names for your Neo4j/Streamlit dashboard!
# =========================================================================

echo "[*] Collecting Entra ID Users..."
# Extracts the Object ID, Email (UPN), and Human Name
az ad user list --query "[].{id:id, principalName:userPrincipalName, displayName:displayName}" --output json > $OUTPUT_DIR/ad_users.json

echo "[*] Collecting Entra ID Service Principals (App Registrations)..."
# Extracts the Object ID and the App Name. 
# Note: Using --all pulls every Microsoft built-in SP too. If it's too slow, remove --all.
az ad sp list --all --query "[].{id:id, displayName:appDisplayName}" --output json > $OUTPUT_DIR/ad_sps.json

echo "[*] Collecting Entra ID Groups..."
# Extracts the Group ID and Group Name
az ad group list --query "[].{id:id, displayName:displayName}" --output json > $OUTPUT_DIR/ad_groups.json

# =========================================================================

echo "[*] Collecting Activity Logs (last 30 days)..."
# Limiting to 1000 events to prevent massive memory usage during graph build
az monitor activity-log list --max-events 1000 --output json > $OUTPUT_DIR/activity_logs.json

echo "[+] Data collection complete. Identity mapping files generated."
