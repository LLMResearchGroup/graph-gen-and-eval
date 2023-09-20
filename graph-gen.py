import random
import networkx as nx
import numpy as np
import json

def reverse_delete(G, d):
    i = 0
    while i < d:
        edges = list(G.edges())
        if len(edges) == 0:
            break
        e = random.choice(edges)
        G.remove_edge(*e)

        if nx.is_connected(G):
            i += 1
        else:
            G.add_edge(*e)
            
def describe_graph(graph):
    nodes = list(graph.nodes())
    nodes_str = " ".join(f"{node}" for node in nodes)

    edges = list(graph.edges())
    edges_str = "->".join([f"{edge[0]}-{edge[1]}" for edge in edges])

    description = f"There is a graph with {len(nodes)} nodes {nodes_str}. The edges are {edges_str}"
    return description

def generate_random_path(graph, length):
    if length < 2:
        raise ValueError("Path length must be at least 2")

    nodes = list(graph.nodes())
    path = [random.choice(nodes)]

    for _ in range(length - 1):
        neighbors = list(graph.neighbors(path[-1]))
        if len(neighbors) <= 1:
          break
        next_node = random.choice(neighbors)
        if next_node in path:
          continue
        path.append(next_node)

    return path

n = 10  # Number of nodes
m = 20  # Number of edges
d = n * (n-1)//2 - m  # Number of edges to delete
G = nx.complete_graph(n)  # Create a complete graph
reverse_delete(G, d)
graph_description = describe_graph(G)
print(graph_description)
random_paths = []
for i in range(30):
    random_path = generate_random_path(G, random.randint(2, n-1))
    random_paths.append(random_path)
print(random_paths)