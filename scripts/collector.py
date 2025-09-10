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
# Build caches
# -------------------
USER_CACHE, SP_CACHE, GROUP_CACHE = {}, {}, {}

def build_cache():
    global USER_CACHE, SP_CACHE, GROUP_CACHE

    # Users → id → displayName
    out = run(["az", "ad", "user", "list", "-o", "json"])
    if out:
        for u in json.loads(out):
            USER_CACHE[u["id"]] = u.get("displayName")

    # Service Principals → id/appId → displayName
    out = run(["az", "ad", "sp", "list", "-o", "json"])
    if out:
        for sp in json.loads(out):
            name = sp.get("displayName") or sp.get("appDisplayName")
            if sp.get("id"):
                SP_CACHE[sp["id"]] = name
            if sp.get("appId"):
                SP_CACHE[sp["appId"]] = name

    # Groups → id → displayName
    out = run(["az", "ad", "group", "list", "-o", "json"])
    if out:
        for g in json.loads(out):
            GROUP_CACHE[g["id"]] = g.get("displayName")

def resolve_principal_name(a):
    pid = a.get("principalId")
    ptype = a.get("principalType")

    if pid in USER_CACHE:
        return USER_CACHE[pid]
    if pid in SP_CACHE:
        return SP_CACHE[pid]
    if pid in GROUP_CACHE:
        return GROUP_CACHE[pid]

    # fallback if still unresolved
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
    build_cache()
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
