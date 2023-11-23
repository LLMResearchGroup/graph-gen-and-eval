# currently defaulted to normal distribution

import random
import networkx
import numpy as np
from enum import Enum


class GraphPrompt(Enum):
    Basic = 1
    Build_A_Graph = 2


class ProbabilityDistribution(Enum):
    Normal = 1
    Uniform = 2


def reverse_delete(
    Graph: networkx.classes.graph.Graph, delete_amount: int
) -> networkx.classes.graph.Graph:
    # Type validity
    if not isinstance(Graph, networkx.classes.graph.Graph) or not isinstance(
        delete_amount, int
    ):
        raise TypeError(
            "Graph must be a networkx.classes.graph.Graph and delete_amount must be an int"
        )

    # Check if the graph is connected
    if not networkx.is_connected(Graph):
        raise ValueError("Graph must be connected")

    # Check if the amount of edge is larger than the delete amount
    if len(Graph.edges()) < delete_amount:
        raise ValueError("Delete amount must be smaller than the amount of edges")

    # Delete Edges: reverse-delete algorithm
    # Reference: https://en.wikipedia.org/wiki/Reverse-delete_algorithm
    for _ in range(delete_amount):
        while True:
            e = random.choice(list(Graph.edges()))
            Graph.remove_edge(*e)
            if networkx.is_connected(Graph):
                break
            Graph.add_edge(*e)


# important for prompt engineering
# description of the graph should be chosen carefully
def describe_graph(
    graph: networkx.classes.graph.Graph, prompt: GraphPrompt = GraphPrompt.Basic
) -> str:
    # Type validity
    if not isinstance(graph, networkx.classes.graph.Graph):
        raise TypeError("Graph must be a networkx.classes.graph.Graph")

    # Basic Prompting
    if prompt == GraphPrompt.Basic:
        nodes = list(graph.nodes())
        nodes_str = " ".join(f"{node}" for node in nodes)

        edges = list(graph.edges())
        edges_str = " ".join([f"{edge[0]}-{edge[1]}" for edge in edges])

        description = f"There is a graph with {len(nodes)} nodes {nodes_str}.\nThe edges are {edges_str}"
        return description

    # Build a graph Prompting
    # Reference:
    # Can Language Models Solve Graph Problems in Natural Language
    # Heng Wang et al.
    # Cite: arXiv:2305.10037 [cs.CL]
    # Link: https://arxiv.org/pdf/2305.10037.pdf
    elif prompt == GraphPrompt.Build_A_Graph:
        nodes = list(graph.nodes())
        num_nodes = len(nodes)
        nodes_str = f"numbered from 0 to {num_nodes - 1}"

        edges = list(graph.edges(data=True))
        edges_str = ""
        for edge in edges:
            source, target, weight = edge[0], edge[1], edge[2].get("weight", "")
            edges_str += f"an edge between node {source} and node {target}"
            if weight:
                edges_str += f" with weight {weight}"
            edges_str += ", "

        description = f"In an undirected graph, the nodes are {nodes_str}, and the edges are:\n{edges_str[:-2]}\nLet's construct a graph with the nodes and edges first."
        return description

    else:
        raise ValueError("Prompt not supported")


def generate_graph(node_number: int, edge_number: int) -> networkx.classes.graph.Graph:
    # Type validity
    if not isinstance(node_number, int) or not isinstance(edge_number, int):
        raise TypeError("Node number and edge number must be int")

    # Check if the node and edge number are valid
    if node_number < 2 or edge_number < 1:
        raise ValueError(
            "Node number must be larger than 1 and edge number must be larger than 0"
        )

    # Check if the edge number is larger than the maximum edge number
    if edge_number > node_number * (node_number - 1) // 2:
        raise ValueError(
            "Edge number must be smaller than the maximum edge number to be connected"
        )

    # Check if edge number is larger than node_number - 1
    if edge_number < node_number - 1:
        raise ValueError(
            "Edge number must be larget than the node number - 1 to be connected"
        )

    deletion_amount = node_number * (node_number - 1) // 2 - edge_number
    Graph = networkx.complete_graph(node_number)
    reverse_delete(Graph, deletion_amount)
    return Graph


def generate_randomly_distributed_path(
    Graph: networkx.classes.graph.Graph,
    sample_size: int,
    distribution: ProbabilityDistribution = ProbabilityDistribution.Normal,
) -> dict:
    # Type validity
    if (
        not isinstance(Graph, networkx.classes.graph.Graph)
        or not isinstance(sample_size, int)
        or not isinstance(distribution, ProbabilityDistribution)
    ):
        raise TypeError(
            "Graph must be a networkx.classes.graph.Graph and sample_size must be an int and distribution must be a ProbabilityDistribution"
        )

    # Check if the graph is connected
    if not networkx.is_connected(Graph):
        raise ValueError("Graph must be connected")

    # Check if the sample size is valid
    if sample_size < 1:
        raise ValueError("Sample size must be larger than 0")

    # Generate random frequencies and path lengths from a normal distribution
    sources = [random.choice(list(Graph.nodes())) for _ in range(sample_size)]
    destinations = [random.choice(list(Graph.nodes())) for _ in range(sample_size)]

    match distribution:
        case ProbabilityDistribution.Normal:
            path_frequencies = [
                # max(1, int(round(random.normalvariate(5, 2))))
                max(1, int(round(random.normalvariate(sample_size/2, sample_size/4))))
                for _ in range(sample_size)
            ]
        case ProbabilityDistribution.Uniform:
            path_frequencies = [
                max(1, int(round(random.uniform(1, 10))))
                for _ in range(sample_size)
            ]
        case _:
            raise ValueError("Distribution not supported")

    # Generate random paths
    path_freq = {}
    for i in range(sample_size):
        path = generate_path(Graph, sources[i], destinations[i])
        if len(path) < 2:
            i = i - 1
            continue
        path_freq[tuple(path)] = path_frequencies[i]
    return path_freq

def generate_path(
    Graph: networkx.classes.graph.Graph, source: int, destination: int
) -> list:
    if (
        not isinstance(Graph, networkx.classes.graph.Graph)
        or not isinstance(source, int)
        or not isinstance(destination, int)
    ):
        raise TypeError(
            "Graph must be a networkx.classes.graph.Graph and source and destination must be int"
        )

    # Check if the graph is connected
    if not networkx.is_connected(Graph):
        raise ValueError("Graph must be connected")

    # Check if the source and destination are valid
    if source < 0 or source >= len(Graph.nodes()):
        raise ValueError("Source must be within the range of the number of nodes")

    if source == destination:
        return [source]
    
    try:
        # Get all simple paths between source and destination
        all_paths = list(
            networkx.all_simple_paths(Graph, source=source, target=destination)
        )

        # Choose a random path from the list of all paths
        if all_paths:
            random_path = random.choice(all_paths)
            return random_path
        else:
            # If there are no paths, return an empty list
            return []
    except networkx.NodeNotFound:
        # If the source or destination node does not exist in the graph, handle the exception
        return []


# test
# node_number = 5  # Number of nodes
# edge_number = 10  # Number of edges
# deletion_amount = (
#     node_number * (node_number - 1) // 2 - edge_number
# )  # Number of edges to delete
# Graph = networkx.complete_graph(node_number)  # Create a complete graph
# reverse_delete(Graph, deletion_amount)
# print(describe_graph(Graph, GraphPrompt.Build_A_Graph))
# print(describe_graph(Graph, GraphPrompt.Basic))
# path_freq = generate_randomly_distributed_path(Graph, 20)
# all_paths = [list(path) for path, freq in path_freq.items() for _ in range(freq)]
# print(all_paths)

__all__ = [
    "generate_graph",
    "describe_graph",
    "GraphPrompt",
    "generate_randomly_distributed_path",
    "ProbabilityDistribution",
]
