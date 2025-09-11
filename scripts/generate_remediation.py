#!/usr/bin/env python3
import json
import os

def main():
    drift_file = "output/drift_report.json"
    remediate_sh = "output/remediate.sh"
    remediation_json = "output/remediation.json"

    if not os.path.exists(drift_file):
        print(f"❌ Missing {drift_file}")
        return

    with open(drift_file) as f:
        report = json.load(f)

    results = report.get("results", [])
    entries = []

    os.makedirs("output", exist_ok=True)

    with open(remediate_sh, "w") as sh:
        sh.write("#!/bin/bash\nset -e\n\n")
        for item in results:
            if item.get("status") == "Fail":
                cmd = f"az role assignment delete --assignee '{item['resourceName']}' --role Owner"
                sh.write(f"# {item['description']}\n{cmd}\n\n")
                entries.append({
                    "Rule ID": item["ruleId"],
                    "Resource name": item["resourceName"],
                    "Remediation script": cmd
                })

    with open(remediation_json, "w") as f:
        json.dump(entries, f, indent=2)

    print(f"✅ Remediation generated:\n - {remediate_sh}\n - {remediation_json}")

if __name__ == "__main__":
    main()
