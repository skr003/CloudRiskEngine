#!/usr/bin/env python3
import json
from collections import Counter

def main():
    with open("output/azure_data.json") as f:
        data = json.load(f)

    results, summary = [], Counter()

    # Group assignments by principal
    principals = {}
    for a in data.get("roleAssignments", []):
        principal = a.get("resourceName", a.get("principalId", "unknown"))
        principals.setdefault(principal, []).append({
            "role": a.get("roleDefinitionName") or a.get("roleDefinitionId", ""),
            "ptype": a.get("principalType", ""),
            "scope": a.get("scope", "")
        })

    # --- Rule checks ---
    for principal, assignments in principals.items():
        roles = [a["role"] for a in assignments]
        ptype = assignments[0].get("ptype", "")

        # Rule 1: High-privileged roles (Owner/Contributor)
        if any("Owner" in r or "Contributor" in r for r in roles):
            status, desc, mitre = "Fail", f"{principal} has high-privileged role", ["T1098"]
        else:
            status, desc, mitre = "Pass", f"{principal} has no high-privileged role", []
        results.append(rule(principal, "IAM-001", desc, status, mitre))
        summary[status.lower()] += 1

        # Rule 2: Service Principal with Owner
        if ptype == "ServicePrincipal" and any("Owner" in r for r in roles):
            status, desc, mitre = "Fail", f"Service Principal {principal} has Owner role", ["T1134.001"]
        else:
            status, desc, mitre = "Pass", f"{principal} has no risky SP privileges", []
        results.append(rule(principal, "IAM-002", desc, status, mitre))
        summary[status.lower()] += 1

        # Rule 3: Too many role assignments (>3)
        if len(roles) > 3:
            status, desc, mitre = "Fail", f"{principal} has {len(roles)} role assignments", ["T1078"]
        else:
            status, desc, mitre = "Pass", f"{principal} has acceptable number of role assignments", []
        results.append(rule(principal, "IAM-003", desc, status, mitre))
        summary[status.lower()] += 1

        # Rule 4: T1078.004 - Valid Accounts: Cloud Accounts (Guest users)
        if "#EXT#" in principal.upper():
            status, desc, mitre = "Fail", f"{principal} is a guest (B2B) user", ["T1078.004"]
        else:
            status, desc, mitre = "Pass", f"{principal} is not a guest user", []
        results.append(rule(principal, "IAM-004", desc, status, mitre))
        summary[status.lower()] += 1

        # Rule 5: T1087.004 - Account Discovery: Cloud Accounts
        suspicious_actions = [
            "microsoft.graph/users/read",
            "microsoft.graph/serviceprincipals/read",
            "microsoft.authorization/roleassignments/read"
        ]
        user_logs = [l for l in data.get("activityLogs", []) if l.get("caller") == principal]
        if any(any(act in json.dumps(l).lower() for act in suspicious_actions) for l in user_logs):
            status, desc, mitre = "Fail", f"{principal} performed suspicious account enumeration", ["T1087.004"]
        else:
            status, desc, mitre = "Pass", f"{principal} has no signs of account enumeration", []
        results.append(rule(principal, "IAM-005", desc, status, mitre))
        summary[status.lower()] += 1

    # Write drift report
    drift = {"results": results, "summary": dict(summary)}
    with open("output/drift_report.json", "w") as f:
        json.dump(drift, f, indent=2)
    print("✅ Drift analysis -> output/drift_report.json")

def rule(principal, rule_id, description, status, mitre):
    return {
        "resourceName": principal,
        "ruleId": rule_id,
        "description": description,
        "status": status,
        "mitre": mitre
    }

if __name__ == "__main__":
    main()
