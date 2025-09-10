#!/usr/bin/env bash
set -euo pipefail

STORAGE_ACCOUNT="cloudriskengine"
CONTAINER="reports"
STORAGE_ACCOUNT_KEY="$STORAGE_ACCOUNT_KEY"
for file in drift_report.json remediation.json remediate.sh privilege_graph.json; do
  az storage blob upload --account-name $STORAGE_ACCOUNT --container-name $CONTAINER --file output/$file --name builds/$BUILD_NUMBER/$file --account-key "$STORAGE_ACCOUNT_KEY" --overwrite
  echo "✅ Uploaded $file"
done
