#!/usr/bin/env python3
import json
from collections import Counter

def main():
    with open("output/azure_data.json") as f:
        data = json.load(f)

    results, summary = [], Counter()

    for a in data.get("roleAssignments", []):
        principal = a.get("principalName") or a.get("principalId", "unknown")
        role_id = a.get("roleDefinitionId", "")
        desc = "Principal has no Owner role"
        status = "Pass"

        if "Owner" in role_id:
            desc = "Principal has Owner role"
            status = "Fail"

        results.append({
            "resourceName": principal,
            "ruleId": "PRIV-001",
            "description": desc,
            "status": status
        })
        summary[status.lower()] += 1

    drift = {"results": results, "summary": dict(summary)}
    with open("output/drift_report.json", "w") as f:
        json.dump(drift, f, indent=2)
    print("✅ Drift analysis -> output/drift_report.json")

if __name__ == "__main__":
    main()
