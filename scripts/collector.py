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
    return json.loads(run(["az", "monitor", "activity-log", "list", "--timespan", timespan, "-o", "json"]))

def main():
    data = {
        "collectedAt": datetime.utcnow().isoformat()+"Z",
        "roleAssignments": collect_role_assignments(),
        "roleDefinitions": collect_role_definitions(),
        "activityLogs": collect_activity_logs(7)
    }
    with open("output/azure_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print("✅ Collected data -> output/azure_data.json")

if __name__ == "__main__":
    main()
