#!/usr/bin/env python3
import json
from collections import Counter

def main():
    with open("output/azure_data.json") as f:
        data = json.load(f)

    results, summary = [], Counter()

    # Group by principal
    principals = {}
    for a in data.get("roleAssignments", []):
        principal = a.get("resourceName", "unknown")
        role = a.get("roleDefinitionName") or a.get("roleDefinitionId", "")
        ptype = a.get("principalType", "")
        scope = a.get("scope", "")
        principals.setdefault(principal, []).append({
            "role": role,
            "ptype": ptype,
            "scope": scope
        })

    # --- Rule checks (applied to every principal) ---
    for principal, assignments in principals.items():
        roles = [a["role"] for a in assignments]
        ptype = assignments[0]["ptype"]

        # Rule 1: Owner/Contributor role should not be assigned
        if any("Owner" in r or "Contributor" in r for r in roles):
            status = "Fail"
            desc = f"{principal} has high-privileged role"
            mitre = ["T1098"]
        else:
            status = "Pass"
            desc = f"{principal} has no high-privileged role"
            mitre = ["T1098"]
        results.append({
            "resourceName": principal,
            "ruleId": "IAM-001",
            "description": desc,
            "status": status,
            "mitre": mitre
        })
        summary[status.lower()] += 1

        # Rule 2: Service Principals should not have Owner
        if ptype == "ServicePrincipal" and any("Owner" in r for r in roles):
            status = "Fail"
            desc = f"Service Principal {principal} has Owner role"
            mitre = ["T1134.001"]
        else:
            status = "Pass"
            desc = f"{principal} has no risky SP privileges"
            mitre = ["T1134.001"]
        results.append({
            "resourceName": principal,
            "ruleId": "IAM-002",
            "description": desc,
            "status": status,
            "mitre": mitre
        })
        summary[status.lower()] += 1

        # Rule 3: Too many role assignments (>3)
        if len(roles) > 3:
            status = "Fail"
            desc = f"{principal} has {len(roles)} role assignments"
            mitre = ["T1078"]
        else:
            status = "Pass"
            desc = f"{principal} has acceptable number of role assignments"
            mitre = ["T1078"]
        results.append({
            "resourceName": principal,
            "ruleId": "IAM-003",
            "description": desc,
            "status": status,
            "mitre": mitre
        })
        summary[status.lower()] += 1

    drift = {"results": results, "summary": dict(summary)}
    with open("output/drift_report.json", "w") as f:
        json.dump(drift, f, indent=2)
    print("✅ Drift analysis -> output/drift_report.json with per-rule Pass/Fail")

if __name__ == "__main__":
    main()
