#!/usr/bin/env python3
import json, subprocess, os
from datetime import datetime, timedelta

def run(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not res.stdout.strip():
        return None
    return res.stdout

def collect_role_assignments():
    out = run(["az", "role", "assignment", "list", "--all", "-o", "json"])
    return json.loads(out) if out else []

def collect_role_definitions():
    out = run(["az", "role", "definition", "list", "-o", "json"])
    return json.loads(out) if out else []

def collect_activity_logs(days=7):
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    timespan = f"{start.isoformat()}Z/{end.isoformat()}Z"
    out = run([
        "az", "monitor", "activity-log", "list",
        "--timespan", timespan, "-o", "json"
    ])
    return json.loads(out) if out else []

# -------------------
# No cache lookups
# -------------------
def resolve_principal_name(a):
    pid = a.get("principalId")
    ptype = a.get("principalType")

    # Try querying Azure AD directly each time
    if ptype == "User":
        out = run(["az", "ad", "user", "show", "--id", pid, "-o", "json"])
    elif ptype == "ServicePrincipal":
        out = run(["az", "ad", "sp", "show", "--id", pid, "-o", "json"])
    elif ptype == "Group":
        out = run(["az", "ad", "group", "show", "--group", pid, "-o", "json"])
    else:
        out = None

    if out:
        obj = json.loads(out)
        return (
            obj.get("displayName")
            or obj.get("appDisplayName")
            or obj.get("userPrincipalName")
            or pid
        )

    # fallback if unresolved
    return (
        a.get("principalDisplayName")
        or a.get("principalName")
        or pid
    )

def enrich_assignments(assignments):
    enriched = []
    for a in assignments:
        a["resourceName"] = resolve_principal_name(a)
        enriched.append(a)
    return enriched

def main():
    assignments = collect_role_assignments()
    role_defs = collect_role_definitions()
    logs = collect_activity_logs(7)

    enriched = enrich_assignments(assignments)

    data = {
        "collectedAt": datetime.utcnow().isoformat() + "Z",
        "roleAssignments": enriched,
        "roleDefinitions": role_defs,
        "activityLogs": logs
    }

    os.makedirs("output", exist_ok=True)
    with open("output/azure_data.json", "w") as f:
        json.dump(data, f, indent=2)

    print("✅ Collected -> output/azure_data.json (resourceName = displayName)")

if __name__ == "__main__":
    main()
