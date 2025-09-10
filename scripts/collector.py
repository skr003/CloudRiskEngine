#!/usr/bin/env python3
import json, subprocess
from datetime import datetime, timedelta

def run(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("Error:", res.stderr)
        return "[]"
    return res.stdout

def collect_role_assignments():
    return json.loads(run(["az", "role", "assignment", "list", "--all", "-o", "json"]))

def collect_role_definitions():
    return json.loads(run(["az", "role", "definition", "list", "-o", "json"]))

def collect_activity_logs(days=7):
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    timespan = f"{start.isoformat()}Z/{end.isoformat()}Z"
    return json.loads(run([
        "az", "monitor", "activity-log", "list",
        "--timespan", timespan, "-o", "json"
    ]))

def enrich_assignments(assignments):
    """Attach friendly names from principalDisplayName when possible"""
    enriched = []
    for a in assignments:
        name = a.get("principalDisplayName") or a.get("principalName") or a.get("principalId")
        a["resourceName"] = name
        enriched.append(a)
    return enriched

def main():
    assignments = collect_role_assignments()
    role_defs = collect_role_definitions()
    logs = collect_activity_logs(7)

    data = {
        "collectedAt": datetime.utcnow().isoformat() + "Z",
        "roleAssignments": enrich_assignments(assignments),
        "roleDefinitions": role_defs,
        "activityLogs": logs
    }
    with open("output/azure_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print("✅ Collected -> output/azure_data.json (with friendly names)")

if __name__ == "__main__":
    main()
