import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
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
