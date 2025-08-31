#!/bin/bash
set -euo pipefail

mkdir -p output/dashboard

cp output/risk_scores.csv output/dashboard/
cp output/escalation_paths.txt output/dashboard/
cp output/mitre_mapping.json output/dashboard/

echo "[*] Data exported to ./output/dashboard for Grafana/Streamlit ingestion."
