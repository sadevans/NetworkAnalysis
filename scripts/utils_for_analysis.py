import networkx as nx
from scipy import stats
import numpy as np


def get_largest_component(G):
    largest_component = max(nx.connected_components(G), key=len)
    return G.subgraph(largest_component)


def get_nodes_degree(G: nx.Graph) -> list:
    node_degree = [v for k, v in G.degree]
    print("Максимальная степень вершины = {}".format(
        max(node_degree))
        )
    print("Средняя степень вершины = {}".format(
        round(np.mean(node_degree), 4))
        )
    return node_degree


def get_network_summary(G):
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    print(f"Количество вершин: {num_nodes}")
    print(f"Количество ребер: {num_edges}")

    largest_cc = get_largest_component(G)

    diameter = nx.diameter(largest_cc)
    radius = nx.radius(largest_cc)
    print(f"Диаметр: {diameter}")
    print(f"Радиус: {radius}")

    node_degree = get_nodes_degree(G)
    global_cc = round(nx.transitivity(G), 4)
    avg_local_cc = round(nx.average_clustering(G), 4)
    print(f"Глобальный коэффициент кластеризации: {global_cc}")
    print(f"Средний локальный коэффициент кластеризации: {avg_local_cc}")

    local_ccs = [nx.clustering(G, node) for node in G.nodes()]

    avg_shortest_path = round(nx.average_shortest_path_length(largest_cc), 4)
    print(f"Средняя длина кратчайшего пути: {avg_shortest_path}")

    shortest_paths = []
    for node in G.nodes():
        for length in nx.shortest_path_length(G, source=node).values():
            shortest_paths.append(length)

    params = stats.powerlaw.fit(node_degree)
    print(f"Параметры распределения степеней вершин: {params}")

    return (local_ccs, shortest_paths, node_degree, params)


def get_model_properties(graph):
    degrees = [degree for node, degree in graph.degree()]
    largest_component = get_largest_component(graph)
    diameter = nx.diameter(get_largest_component(largest_component))
    clustering = nx.average_clustering(largest_component)
    avg_path = nx.average_shortest_path_length(largest_component) if nx.is_connected(largest_component) else "Граф не связный"
    return diameter, clustering, avg_path


def print_model_properties(model_name: str = 'ER', properties: list = []):
    print(f"\nСвойства {model_name} модели:")
    # print(f"  Распределение степеней: {properties[0]}")
    print(f"  Диаметр: {properties[0]}")
    print(f"  Коэффициент кластеризации: {round(properties[1], 4)}")
    print(f"  Средний кратчайший путь: {round(properties[2], 4)}")


def compare_network_models(G: nx.Graph, node_degrees: list, p: float, m_ba: int, p_ws: float = 0.4):
    n = G.number_of_nodes()
    er_graph = nx.erdos_renyi_graph(n, p)
    ba_graph = nx.barabasi_albert_graph(n, m_ba)
    k = int(round(np.mean(node_degrees)))
    p_ws = 0.4
    ws_graph = nx.watts_strogatz_graph(n, k, p_ws)

    config_model = nx.Graph(nx.configuration_model(node_degrees))

    er_props = get_model_properties(er_graph)
    ba_props = get_model_properties(ba_graph)
    ws_props = get_model_properties(ws_graph)
    config_model_props = get_model_properties(config_model)
    print_model_properties(model_name='ER', properties=er_props)
    print_model_properties(model_name='BA', properties=ba_props)
    print_model_properties(model_name='WS', properties=ws_props)
    print_model_properties(model_name='Configuration Model', properties=config_model_props)
    return er_props, ba_props, ws_props, config_model_props


def calculate_difference(real_props: list, model_props: list):
    diameter_diff = abs(real_props[0] - model_props[0])
    clustering_diff = abs(real_props[1] - model_props[1])
    path_diff = 0
    if real_props[2] != "Граф не связный" and model_props[2] != "Граф не связный":
        path_diff = abs(real_props[2] - model_props[2])
    return diameter_diff, clustering_diff, path_diff


def compare_graphs(graph):
    n = nx.number_of_nodes(graph)
    m = nx.number_of_edges(graph)
    k = np.mean([v for k, v in graph.degree()])
    erdos = nx.erdos_renyi_graph(n, p=m / float(n * (n - 1) / 2))
    barabasi = nx.barabasi_albert_graph(n, m=int(k) - 7)
    small_world = nx.watts_strogatz_graph(n, int(k), p=0.04)
    print(" ")
    print("Compare the number of edges")
    print(" ")
    print("My network: " + str(nx.number_of_edges(graph)))
    print("Erdos: " + str(nx.number_of_edges(erdos)))
    print("Barabasi: " + str(nx.number_of_edges(barabasi)))
    print("SW: " + str(nx.number_of_edges(small_world)))
    print(" ")
    print("Compare average clustering coefficients")
    print(" ")
    print("My network: " + str(nx.average_clustering(graph)))
    print("Erdos: " + str(nx.average_clustering(erdos)))
    print("Barabasi: " + str(nx.average_clustering(barabasi)))
    print("SW: " + str(nx.average_clustering(small_world)))
    print(" ")
    print("Compare average path length")
    print(" ")
    for i, c in enumerate(nx.connected_components(graph)):
        conn_g = graph.subgraph(c)
        print(f'My network {i}: ' + str(nx.average_shortest_path_length(conn_g)))
    print("Erdos: " + str(nx.average_shortest_path_length(erdos)))
    print("Barabasi: " + str(nx.average_shortest_path_length(barabasi)))
    print("SW: " + str(nx.average_shortest_path_length(small_world)))
    print(" ")
    print("Compare graph diameter")
    print(" ")
    for i, c in enumerate(nx.connected_components(graph)):
        conn_g = graph.subgraph(c)
        print(f'My network {i}: ' + str(nx.diameter(conn_g)))
    print("Erdos: " + str(nx.diameter(erdos)))
    print("Barabasi: " + str(nx.diameter(barabasi)))
    print("SW: " + str(nx.diameter(small_world)))


    return erdos, barabasi, small_world
