import json
import os

# Configuration
ROLE_FILE = "output/role_definitions.json"
MITRE_CONFIG = "config/mitre_mapping.json"
OUTPUT_FILE = "output/mitre_mapping.json"

def main():
    # 1. Load the MITRE mapping config
    if not os.path.exists(MITRE_CONFIG):
        print(f"Error: {MITRE_CONFIG} not found.")
        return

    with open(MITRE_CONFIG, 'r') as f:
        # Normalize keys: ensure no trailing wildcards interfere
        raw_mapping = json.load(f)
        mitre_map = {k.lower(): v for k, v in raw_mapping.items()}

    # 2. Load Role Definitions
    if not os.path.exists(ROLE_FILE):
        print(f"Error: {ROLE_FILE} not found. Run 'az role definition list' first.")
        return

    print("[*] Loading Azure Roles (this may take a moment)...")
    try:
        with open(ROLE_FILE, 'r') as f:
            roles = json.load(f)
    except json.JSONDecodeError:
        print("Error: role_definitions.json is corrupt. Please regenerate it.")
        return

    results = []
    print("[*] Mapping Actions to MITRE TTPs...")

    # 3. Iterate and Match
    for role in roles:
        role_name = role.get('roleName', 'Unknown')
        
        # Combine actions and dataActions, filter out None/Empty
        permissions = role.get('permissions', [])
        all_actions = []
        for perm in permissions:
            all_actions.extend(perm.get('actions', []))
            all_actions.extend(perm.get('dataActions', []))

        for action in all_actions:
            # Normalize action to lowercase for matching
            action_lower = action.lower()
            
            # Check 1: Exact Match
            ttp = mitre_map.get(action_lower)

            # Check 2: Wildcard Match (if exact fails)
            # e.g., Microsoft.Compute/virtualMachines/* -> should match specific map keys? 
            # Usually we map specific ACTIONS to TTPs. 
            # If the mapping has "microsoft.compute/virtualmachines/write", 
            # and the role has that exact action, we match.
            
            if ttp:
                results.append({
                    "role": role_name,
                    "action": action,
                    "ttp": ttp
                })

    # 4. Write Output
    print(f"[*] Found {len(results)} matches.")
    with open(OUTPUT_FILE, 'w') as f:
        # Writing as a JSON Array
        json.dump(results, f, indent=2)
    
    print(f"[*] Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
