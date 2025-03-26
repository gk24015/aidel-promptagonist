from db.neo4j_connect import execute_query

def view_relationships(node1, node2):
    query = """
    MATCH (n {name: $node1})-[r]-(m {name: $node2})
    RETURN n.name AS Node1, type(r) AS Relationship, m.name AS Node2
    """
    params = {"node1": node1, "node2": node2}
    results = execute_query(query, params)

    if results:
        print(f"Relationships between '{node1}' and '{node2}':")
        for result in results:
            print(f"{result['Node1']} -[{result['Relationship']}]-> {result['Node2']}")
    else:
        print(f"No relationships found between '{node1}' and '{node2}'.")


