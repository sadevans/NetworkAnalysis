import time
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import scipy.spatial as spt


def find_top_nodes(g, values, number):
    print(values)
    sorted_values = sorted(values, key=lambda x: x[1], reverse=True)
    print(sorted_values)
    best = {i[0]: g.nodes[i[0]]["domain"] for i in sorted_values[0:number]}
    return best


def draw_graph(g, parameter, size_of_nodes, number):
    """
    draws plot according to parameter of interest and size of nodes
    """
    node_labels = find_top_nodes(g, parameter, number)
    plt.xkcd()
    plt.figure(1, figsize=(30, 25))
    coord = nx.spring_layout(g)
    nx.draw(
        g,
        pos=coord,
        nodelist=parameter.keys(),
        node_size=[d * size_of_nodes for d in parameter.values()],
        node_color=list(parameter.values()),
        font_size=25,
        cmap=plt.cm.get_cmap("RdBu_r"),
        labels=node_labels,
    )

def create_df_with_param(g, parameter: dict={}, parameter_name: str='parameter'):
    df = pd.DataFrame(g.nodes.values())
    
    if len(parameter) != 0:
        print(parameter)
        # df_degree = pd.DataFrame(parameter, columns=['id', parameter_name])
        df_degree
        print(df_degree)
        df = pd.merge(df, df_degree,how="left")
        df = df.sort_values(parameter_name, ascending=False)
        columns = ["id", "domain", "sex", "first_name", "last_name", "university_name", "city_title", parameter_name]
        for i, col in enumerate(columns):
            if col not in df.columns:
                columns.pop(i)
                print("Scipping: ", col)
        df = df[columns]
        # df = df.set_index('id')
    # else:
    #     df =df.set_index('id')
    return df


def get_node_labels(df: pd.DataFrame, number: int=-1):
    node_labels = df[:number].T.to_dict('list')
    node_labels = {k: f'{label[0]}_{label[1]}_{label[2]}' if type(label[2]) == str else f'{label[0]}_{label[1]}' for k, label in node_labels.items()}
    return node_labels



def show_graph(g, parameter: dict={}, size_of_nodes=1000, number=15, figsize=(40,25), parameter_name: str='parameter', save_file: str = '', show: bool=True):
    lespos = nx.kamada_kawai_layout(g)
    sorted_df = create_df_with_param(g, parameter, parameter_name=parameter_name)
    labels_df = sorted_df[['first_name', 'last_name', 'city_title']]
    plt.figure(1, figsize=figsize)
    if len(parameter) != 0:
        node_labels = get_node_labels(labels_df, number)
        nx.draw(
            g,
            pos=lespos,
            node_size=[v * size_of_nodes for k, v in parameter],
            node_color=[v for k, v in parameter],
            font_size=25,
            cmap=plt.cm.get_cmap("RdBu_r"),
            labels=node_labels,
        )
    else:
        node_labels = get_node_labels(labels_df)
        nx.draw(
                g,
                pos=lespos,
                node_color='white',
                edgecolors='black',
                node_size=size_of_nodes,
                font_size=25,
                # cmap=plt.cm.get_cmap("RdBu_r"),
                labels=node_labels,
            )
    plt.title("Graph of Friends Connections", fontsize=40)
    if save_file != '':
        plt.savefig(save_file)
    if show:
        plt.show()
    return sorted_df