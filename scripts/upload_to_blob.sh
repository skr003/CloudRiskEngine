#!/usr/bin/env bash
set -euo pipefail

STORAGE_ACCOUNT=${STORAGE_ACCOUNT:-"cloudriskengine"}
CONTAINER=${CONTAINER:-"reports"}

for file in drift_report.json remediation.json remediate.sh privilege_graph.json; do
  az storage blob upload \
    --account-name $STORAGE_ACCOUNT \
    --container-name $CONTAINER \
    --file output/$file \
    --name $file \
    --overwrite
  echo "✅ Uploaded $file"
done
