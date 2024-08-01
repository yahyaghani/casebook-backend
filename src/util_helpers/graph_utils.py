def parse_to_graph(casename_list, citation_list, provision_list):
    nodes = [{"id": "MAIN", "label": "Main", "group": "ROOT"}]
    links = []

    # Add main category nodes
    category_nodes = ["CASENAME", "CITATION", "PROVISION"]
    for category in category_nodes:
        nodes.append({"id": category, "label": category.capitalize(), "group": "CATEGORY"})
        links.append({"source": "MAIN", "target": category, "label": "Contains"})

    # Add nodes from casename_list and link to CASENAME
    for casename, _ in casename_list[:10]:
        nodes.append({"id": casename, "label": casename, "group": "CASENAME"})
        links.append({"source": "CASENAME", "target": casename, "label": "Includes"})

    # Add nodes from citation_list and link to CITATION
    for citation, _ in citation_list[:10]:
        nodes.append({"id": citation, "label": citation, "group": "CITATION"})
        links.append({"source": "CITATION", "target": citation, "label": "Includes"})

    # Add nodes from provision_list and link to PROVISION
    for provision, _ in provision_list[:10]:
        nodes.append({"id": provision, "label": provision, "group": "PROVISION"})
        links.append({"source": "PROVISION", "target": provision, "label": "Includes"})

    return {"nodes": nodes, "links": links}
