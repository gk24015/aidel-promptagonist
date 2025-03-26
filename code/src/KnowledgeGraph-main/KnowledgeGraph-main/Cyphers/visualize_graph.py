import networkx as nx
import matplotlib.pyplot as plt
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

# Establish Neo4j connection
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def fetch_graph():
    query = """
    MATCH (n)-[r]->(m)
    RETURN n.name AS source, m.name AS target, type(r) AS relationship
    """
    with driver.session() as session:
        result = session.run(query)
        return [(record['source'], record['target'], record['relationship']) for record in result]

def visualize_graph():
    G = nx.MultiDiGraph()  # MultiDiGraph for multiple relationships
    relationships = fetch_graph()

    for source, target, relationship in relationships:
        if source is None or target is None:
            print(f"Skipped node with missing data: {source}, {target}")
            continue
        G.add_edge(source, target, label=relationship)

    pos = nx.spring_layout(G, seed=42)  # Consistent layout
    plt.figure(figsize=(12, 8))

    nx.draw(G, pos, with_labels=True, node_size=3000, node_color='skyblue', font_size=10, font_weight='bold', arrows=True, edge_color='gray')

    # Draw all edge labels for each edge (handles multiple labels)
    edge_labels = {(u, v): [G[u][v][k]['label'] for k in G[u][v]] for u, v in G.edges()}
    formatted_labels = {(u, v): ', '.join(labels) for (u, v), labels in edge_labels.items()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=formatted_labels, font_color='red')

    output_path = os.path.join(os.getcwd(), 'images', 'graph_visualization.png')
    plt.savefig(output_path)
    plt.close()

visualize_graph()
driver.close()
