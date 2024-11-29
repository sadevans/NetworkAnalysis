import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from matplotlib.lines import Line2D
import pandas as pd
sns.set(style="darkgrid", palette="deep", font_scale=1.2)


def plot_characteristic(
        characteristic: list,
        title: str = '',
        xlabel: str = '',
        ylabel: str = 'frequency',
        bins: int = 50,
        color: str = '',
):

    plt.hist(characteristic, bins=bins, color=color)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()



def create_df_with_param(g, parameter: dict={}, parameter_name: str='parameter'):
    df = pd.DataFrame(g.nodes.values())
    df = df[df['vk_id'].notna()]
    df['vk_id'] = df['vk_id'].astype('int')
    if len(parameter) != 0:
        print(parameter)
        df_degree = pd.DataFrame(parameter, columns=['vk_id', parameter_name])
        print(df_degree)
        df = pd.merge(df, df_degree,how="left")
        df = df.sort_values(parameter_name, ascending=False)
        columns = ["vk_id", "name", "domain", "sex", "first_name", "last_name", "university_name", "city_title", parameter_name]
        for i, col in enumerate(columns):
            if col not in df.columns:
                columns.pop(i)
                print("Scipping: ", col)
        df = df[columns]
        df = df.set_index('vk_id')
    else:
        df =df.set_index('vk_id')
    return df

def get_node_labels(df: pd.DataFrame, number: int=-1):
    node_labels = df[:number].T.to_dict('list')
#     for k, label in node_labels.items():
        # print(label)
    node_labels = {k: f'{label[0]}' for k, label in node_labels.items()}
    return node_labels



# def show_graph(g, parameter: dict={}, size_of_nodes=1000, number=15, figsize=(40,25), parameter_name: str='parameter', save_file: str = '', show: bool=True):
#     lespos = nx.kamada_kawai_layout(g)
#     sorted_df = create_df_with_param(g, parameter, parameter_name=parameter_name)
#     labels_df = sorted_df[['name']]
#     plt.figure(1, figsize=figsize)
#     if len(parameter) != 0:
#         node_labels = get_node_labels(labels_df, number)
#         nx.draw(
#             g,
#             pos=lespos,
#             node_size=[v * size_of_nodes for k, v in parameter],
#             node_color=[v for k, v in parameter],
#             font_size=25,
#             cmap=plt.cm.get_cmap("RdBu_r"),
#             labels=node_labels,
#         )
#     else:
#         node_labels = get_node_labels(labels_df)
#         nx.draw(
#                 g,
#                 pos=lespos,
#                 node_color='white',
#                 edgecolors='black',
#                 node_size=size_of_nodes,
#                 font_size=25,
#                 cmap=plt.cm.get_cmap("RdBu_r"),
#                 labels=node_labels,
#             )
#     plt.title("Graph of Friends Connections", fontsize=40)
#     if save_file != '':
#         plt.savefig(save_file)
#     if show:
#         plt.show()
#     return sorted_df



def get_node_labels(labels_df, number=None):
    if number is not None:
        node_labels = labels_df.nlargest(number, 'parameter')['name'].to_dict()
    else:
        node_labels = labels_df['name'].to_dict()
    return {k: v for k, v in node_labels.items()}


def show_graph(g, parameter: dict={}, size_of_nodes=1000, number=15, figsize=(40,25), parameter_name: str='parameter', save_file: str = '', show: bool=True):
    lespos = nx.kamada_kawai_layout(g)
    sorted_df = create_df_with_param(g, parameter, parameter_name=parameter_name)
    labels_df = sorted_df[['name']]
    node_labels = {node: g.nodes[node].get('name', str(node)) for node in g.nodes()}
    plt.figure(1, figsize=figsize)
    if len(parameter) != 0:
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
        nx.draw(
                g,
                pos=lespos,
                node_color='white',
                edgecolors='black',
                node_size=size_of_nodes,
                font_size=25,
                cmap=plt.cm.get_cmap("RdBu_r"),
                labels=node_labels,
            )
    # plt.title("Graph of Friends Connections", fontsize=40)
    if save_file != '':
        plt.savefig(save_file)
    if show:
        plt.show()
    return sorted_df

