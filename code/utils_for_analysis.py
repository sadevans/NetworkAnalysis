import numpy as np
import networkx as nx
# import scipy
import scipy.stats as stats
from collections import Counter
import time


def graph_summary(graph: nx.Graph) -> str:
    return f"Graph Summary:\n- Number of nodes: {graph.number_of_nodes()}\n- Number of edges: {graph.number_of_edges()}"


def get_nodes_degree(G: nx.Graph) -> list:
    node_degree = [v for k, v in G.degree]
    print("Максимальная степень вершины = {}".format(
        max(node_degree))
        )
    print("Средняя степень вершины = {}".format(
        round(np.mean(node_degree), 4))
        )
    return node_degree


def get_basic_information(g: nx.Graph) -> None:
    print(
        "Network has {} nodes with {} connections between each other.".format(
            g.number_of_nodes(), g.number_of_edges()
        )
    )

    print("Number of connected components = {}".format(
        nx.number_connected_components(g))
        )


def get_network_summary(G: nx.Graph):
    # Количество вершин и ребер
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    print(f"Количество вершин: {num_nodes}")
    print(f"Количество ребер: {num_edges}")

    # Диаметр и радиус
    diameter = nx.diameter(G)
    radius = nx.radius(G)
    print(f"Диаметр: {diameter}")
    print(f"Радиус: {radius}")

    node_degree = get_nodes_degree(G)

    # Коэффициент кластеризации
    global_cc = round(nx.transitivity(G), 4)
    avg_local_cc = round(nx.average_clustering(G), 4)
    print(f"Глобальный коэффициент кластеризации: {global_cc}")
    print(f"Средний локальный коэффициент кластеризации: {avg_local_cc}")

    local_ccs = [nx.clustering(G, node) for node in G.nodes()]

    avg_shortest_path = round(nx.average_shortest_path_length(G), 4)
    print(f"Средняя длина кратчайшего пути: {avg_shortest_path}")

    shortest_paths = []
    for node in G.nodes():
        for length in nx.shortest_path_length(G, source=node).values():
            shortest_paths.append(length)

    # degrees = [G.degree(node) for node in G.nodes()]

    params = stats.powerlaw.fit(node_degree)
    print(f"Параметры распределения степеней вершин: {params}")

    return (local_ccs, shortest_paths, node_degree, params)


def get_model_properties(graph):
    degrees = [degree for node, degree in graph.degree()]
    degree_counts = Counter(degrees)
    clustering = nx.average_clustering(graph)
    avg_path = nx.average_shortest_path_length(graph) if nx.is_connected(graph) else "Граф не связный"
    return degree_counts, clustering, avg_path


def print_model_properties(model_name: str = 'ER', properties: list = []):
    print(f"\nСвойства {model_name} модели:")
    print(f"  Распределение степеней: {properties[0]}")
    print(f"  Коэффициент кластеризации: {properties[1]}")
    print(f"  Средний кратчайший путь: {properties[2]}")


def compare_network_models(G: nx.Graph, node_degrees: list, p: float, m_ba: int, p_ws: float = 0.4):

    # ER модель
    n = G.number_of_nodes()
    # m = G.number_of_edges()
    # p = (2 * m) / (n * (n - 1))
    er_graph = nx.erdos_renyi_graph(n, p)

    # BA модель
    # m_ba = int(round(m / n))
    ba_graph = nx.barabasi_albert_graph(n, m_ba)

    # WS модель
    k = int(round(np.mean(node_degrees)))
    p_ws = 0.4
    ws_graph = nx.watts_strogatz_graph(n, k, p_ws)

    er_props = get_model_properties(er_graph)
    ba_props = get_model_properties(ba_graph)
    ws_props = get_model_properties(ws_graph)

    print_model_properties(model_name='ER', properties=er_props)
    print_model_properties(model_name='BA', properties=ba_props)
    print_model_properties(model_name='WS', properties=ws_props)

    return er_props, ba_props, ws_props


def calculate_difference(real_props: list, model_props: list):
    degree_diff = sum([(real_props[0].get(deg, 0) - model_props[0].get(deg, 0))**2 for deg in set(real_props[0]) | set(model_props[0])])
    clustering_diff = abs(real_props[1] - model_props[1])
    path_diff = 0
    if real_props[2] != "Граф не связный" and model_props[2] != "Граф не связный":
        path_diff = abs(real_props[2] - model_props[2])
    return degree_diff, clustering_diff, path_diff
