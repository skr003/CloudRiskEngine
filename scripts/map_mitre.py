import json
import os

ROLE_FILE = "output/role_definitions.json"
MITRE_CONFIG = "config/mitre_mapping.json" # Your manual mapping config
OUTPUT_FILE = "output/mitre_matches.json"

def main():
    print("[*] [Module 3] Mapping Actions to MITRE TTPs...")
    
    # Load Mapping Config (Ensure this file exists in your repo)
    with open(MITRE_CONFIG, 'r') as f:
        mitre_map = {k.lower(): v for k, v in json.load(f).items()}

    # Load Roles
    with open(ROLE_FILE, 'r') as f:
        roles = json.load(f)

    results = []
    for role in roles:
        role_name = role.get('roleName')
        permissions = role.get('permissions', [])
        
        for perm in permissions:
            actions = perm.get('actions', []) + perm.get('dataActions', [])
            for action in actions:
                # Check for match
                ttp = mitre_map.get(action.lower())
                # Handle wildcards if needed (simplified here)
                if not ttp and action.endswith("/*"):
                     ttp = mitre_map.get(action[:-2].lower())

                if ttp:
                    results.append({"role": role_name, "action": action, "ttp": ttp})

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[+] Found {len(results)} TTP mappings.")

if __name__ == "__main__":
    main()
