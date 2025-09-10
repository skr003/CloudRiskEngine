#!/usr/bin/env python3
import json
import networkx as nx

def main():
    with open("output/azure_data.json") as f:
        data = json.load(f)

    G = nx.DiGraph()

    # Build nodes & edges
    for a in data.get("roleAssignments", []):
        principal = a.get("principalName") or a.get("principalId", "unknown")
        role = a.get("roleDefinitionId", "unknown")
        scope = a.get("scope", "subscription")

        G.add_node(principal, type="Principal")
        G.add_node(role, type="Role")
        G.add_node(scope, type="Resource")

        G.add_edge(principal, role, relation="ASSIGNED")
        G.add_edge(role, scope, relation="APPLIES_TO")

    # Export JSON graph
    graph_json = {
        "nodes": [{"id": n, "type": G.nodes[n].get("type")} for n in G.nodes()],
        "links": [{"source": u, "target": v, "relation": d["relation"]} for u,v,d in G.edges(data=True)]
    }
    with open("output/privilege_graph.json", "w") as f:
        json.dump(graph_json, f, indent=2)
    print("✅ Graph -> output/privilege_graph.json")

if __name__ == "__main__":
    main()
