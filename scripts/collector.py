#!/usr/bin/env python3
import json, subprocess
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
    out = run(["az", "monitor", "activity-log", "list", "--timespan", timespan, "-o", "json"])
    return json.loads(out) if out else []

# --- Global caches ---
USER_CACHE = {}
SP_CACHE = {}
GROUP_CACHE = {}

def build_cache():
    global USER_CACHE, SP_CACHE, GROUP_CACHE

    # Users
    out = run(["az", "ad", "user", "list", "-o", "json"])
    if out:
        for u in json.loads(out):
            USER_CACHE[u["id"]] = u.get("displayName") or u.get("userPrincipalName")

    # Service Principals (map both objectId and appId → name)
    out = run(["az", "ad", "sp", "list", "-o", "json"])
    if out:
        for sp in json.loads(out):
            name = sp.get("displayName") or sp.get("appDisplayName")
            if sp.get("id"):     # objectId
                SP_CACHE[sp["id"]] = name
            if sp.get("appId"):  # appId
                SP_CACHE[sp["appId"]] = name

    # Groups
    out = run(["az", "ad", "group", "list", "-o", "json"])
    if out:
        for g in json.loads(out):
            GROUP_CACHE[g["id"]] = g.get("displayName")

def resolve_principal_name(pid, ptype):
    """Resolve principalId into a human-friendly name via caches"""
    if not pid:
        return "unknown"

    if ptype == "User" and pid in USER_CACHE:
        return USER_CACHE[pid]
    elif ptype == "ServicePrincipal" and pid in SP_CACHE:
        return SP_CACHE[pid]
    elif ptype == "Group" and pid in GROUP_CACHE:
        return GROUP_CACHE[pid]
    else:
        return pid  # fallback to ID

def enrich_assignments(assignments):
    enriched = []
    for a in assignments:
        pid = a.get("principalId")
        ptype = a.get("principalType")
        name = resolve_principal_name(pid, ptype)
        a["resourceName"] = name
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

    with open("output/azure_data.json", "w") as f:
        json.dump(data, f, indent=2)

    print("✅ Collected -> output/azure_data.json (user/SP/group names resolved where possible)")

if __name__ == "__main__":
    main()
