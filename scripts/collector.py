#!/usr/bin/env python3
import json, subprocess, os
from datetime import datetime, timedelta

def run(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
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

# Load manual SP mapping
SP_FALLBACK = {}
if os.path.exists("sp_mapping.json"):
    with open("sp_mapping.json") as f:
        SP_FALLBACK = json.load(f)

UNRESOLVED_SPS = set()

def resolve_principal_name(a):
    pid = a.get("principalId")
    ptype = a.get("principalType")

    # Service Principals
    if ptype == "ServicePrincipal":
        if pid in SP_FALLBACK:
            return SP_FALLBACK[pid]
        UNRESOLVED_SPS.add(pid)
        return pid

    # Users / Groups: fall back to principalName or displayName
    return (
        a.get("principalDisplayName")  # if available
        or a.get("principalName")      # usually UPN/mail
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

    # Save unresolved SPs for manual mapping
    if UNRESOLVED_SPS:
        with open("output/unresolved_sps.json", "w") as f:
            json.dump(sorted(list(UNRESOLVED_SPS)), f, indent=2)
        print(f"⚠️ Unresolved SPs written to output/unresolved_sps.json")

    print("✅ Collected -> output/azure_data.json")

if __name__ == "__main__":
    main()
