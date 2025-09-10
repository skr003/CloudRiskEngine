#!/usr/bin/env python3
import json

def main():
    with open("output/drift_report.json") as f:
        report = json.load(f)

    entries = []
    with open("output/remediate.sh", "w") as sh:
        sh.write("#!/bin/bash\nset -e\n\n")
        for item in report["results"]:
            if item["status"] == "Fail":
                cmd = f"az role assignment delete --assignee '{item['resourceName']}' --role Owner"
                sh.write(f"# {item['description']}\n{cmd}\n\n")
                entries.append({
                    "Rule ID": item["ruleId"],
                    "Resource name": item["resourceName"],
                    "Remediation script": cmd
                })

    with open("output/remediation.json", "w") as f:
        json.dump(entries, f, indent=2)
    print("✅ Remediation -> output/remediation.json & output/remediate.sh")

if __name__ == "__main__":
    main()
