#!/bin/bash
set -euo pipefail

INPUT="output/risk_scores.csv"
FIX_FILE="output/remediation.tf"

echo "# Auto-generated Terraform Remediation" > $FIX_FILE

cat $INPUT | tail -n +2 | while IFS=, read -r principal role score; do
  if [[ "$role" =~ "Owner" || "$role" =~ "Contributor" ]]; then
    echo "resource \"azurerm_role_assignment\" \"fix_${principal}\" {
      scope              = \"/subscriptions/<SUBSCRIPTION_ID>\"
      role_definition_name = \"Reader\"
      principal_id       = \"$principal\"
    }" >> $FIX_FILE
  fi
done

echo "[*] Remediation plan written to $FIX_FILE"
