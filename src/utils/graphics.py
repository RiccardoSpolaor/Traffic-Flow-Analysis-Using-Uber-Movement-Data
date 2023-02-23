import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib import cm, colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
import networkx as nx
import numpy as np
from typing import Dict

from utils.metrics import normalize_centrality_measures, get_modularity_score
from utils.geodataframe import get_geodataframe_coordinates_dict
from utils.metrics import normalize_centrality_measures

def plot_spatial_network(gdf: gpd.GeoDataFrame, spatial_network: nx.Graph, title: str = 'Spatial network') -> None:
    """Plot the spatial network on the map of the city.

    Parameters
    ----------
    gdf : GeoDataFrame
        The geodataframe containing relevant geographic information of the city areas.
    spatial_network : Graph
        The spatial network
    title : str, optional
        The title of the plot, by default 'Spatial network'
    """
    _, ax = plt.subplots(1, 1, figsize=(15, 10))

    gdf.plot(ax=ax, edgecolor='darkgray', color='white')

    coordinates = get_geodataframe_coordinates_dict(gdf)

    nx.draw(
        spatial_network,
        coordinates,
        ax=ax,
        node_size=20,
        width=1,
        node_color="black",
        edge_color="black",
        alpha=.6,
    )

    plt.title(title)

    plt.show()
    
def plot_normalized_temporal_centralities(gdf: gpd.GeoDataFrame, spatial_network: nx.Graph, 
                                          centrality_dict: Dict[int, Dict[str, float]], city_name: str, metric_name: str,
                                          cmap: colors.LinearSegmentedColormap = plt.cm.YlGnBu) -> None:
    """Plot the centrality measures of a series of temporal networks over the city map.
    These centralities are normalized by a min-max scale across all the networks.

    Parameters
    ----------
    gdf : GeoDataFrame
        The geodataframe containing relevant geographic information of the city areas.
    spatial_network : Graph
        The spatial network of the city.
    centrality_dict :  { int: { str: float } }
        The dictionary containing for each temporal network (key) a dictionary (value) with information about the centrality values of their nodes.
    city_name : str
        The city name.
    metric_name : str
        The metric name.
    cmap : LinearSegmentedColormap, optional
        Colormap to use, by default YlGnBu.
    """
    centrality_dict = normalize_centrality_measures(centrality_dict)

    for k, v in centrality_dict.items():
        plot_centrality(gdf, spatial_network, v, title = f"{city_name}'s {metric_name} centrality at {k:02d}:00", cmap=cmap)

def plot_centrality(gdf: gpd.GeoDataFrame, spatial_network: nx.Graph, metric_dictionary: Dict[str, float],
                title: str = 'Metric plot', cmap: colors.LinearSegmentedColormap = plt.cm.YlGnBu) -> None:
    """Plot the centrality measure of the nodes over the city map.

    Parameters
    ----------
    gdf : GeoDataFrame
        The geodataframe containing relevant geographic information of the city areas.
    spatial_network : nx.Graph
        The spatial network of the city.
    metric_dictionary : { str, float }
        Dictionary that for each node (key) contains its centrality value (value)
    title : str, optional
        The title of the plot, by default 'Metric plot'
    cmap : LinearSegmentedColormap, optional
        Colormap to use, by default YlGnBu
    """
    fig, ax = plt.subplots(1, figsize=(15, 10))

    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='2%', pad=-.0005)

    gdf.plot(ax=ax, edgecolor='darkgray', color='lightgray')

    coordinates = get_geodataframe_coordinates_dict(gdf)
    node_colors = [metric_dictionary[n] if n in metric_dictionary.keys() else 0 for n in spatial_network.nodes()]

    nx.draw(
        spatial_network,
        coordinates,
        ax=ax,
        node_size=30,
        width=.5,
        node_color=node_colors,
        edge_color="white",
        style='--',
        alpha=.8,
        cmap=cmap,
        vmin=0,
        vmax=1
    )

    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    norm = colors.Normalize(vmin=0, vmax=1)
    fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)

    ax.set_title(title)

    plt.show()

def plot_communities(gdf: gpd.GeoDataFrame, spatial_network: nx.Graph, community_dictionary: Dict[str, int],
                     title: str = 'Metric plot', cmap: colors.ListedColormap = plt.cm.tab10) -> None:
    """Plot the communities of the nodes over the city map.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        The geodataframe containing relevant geographic information of the city areas.
    spatial_network : nx.Graph
        The spatial network of the city.
    community_dictionary : { str: int }
        Dictionary that for each node (key) contains its community (value)
    title : str, optional
        The title of the plot, by default 'Metric plot'
    cmap : ListedColormap, optional
        Colormap to use, by default tab10
    """
    _, ax = plt.subplots(1, figsize=(15, 10))

    gdf.plot(ax=ax, edgecolor='darkgray', color='lightgray')

    coordinates = get_geodataframe_coordinates_dict(gdf)
    
    gray = (.5, .5, .5, 1)
    
    node_colors = [cmap(community_dictionary[n]) if n in community_dictionary.keys() else gray
                   for n in spatial_network.nodes()]

    nx.draw(
        spatial_network,
        coordinates,
        ax=ax,
        node_size=30,
        width=.5,
        node_color=node_colors,
        edge_color="white",
        style='--',
        alpha=.8,
    )

    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    if gray in node_colors:
        legend_elements = [Line2D([0], [0], marker='o', color='white', label='Unknown community', 
                                markerfacecolor=gray, markersize=8)]

        ax.legend(handles=legend_elements, loc='lower right')

    ax.set_title(title)

    plt.show()

def plot_temporal_network_centrality_distribution(centralities: Dict[int, Dict[str, float]], metric: str):
    """Plot the centrality distibution and the cumulative centrality distribution in the temporal network.

    Parameters
    ----------
    centralities : { int: { str: float }}
        The dictionary containing for each temporal network (key) a dictionary (value) with information about the centrality values of their nodes.
    metric : str
        The name of the centrality metric.
    """
    centralities = normalize_centrality_measures(centralities)

    # Histogram
    histograms = dict()
    bins = dict()
    
    for k, v in centralities.items():
        hist, bin_edges = np.histogram(list(v.values()), bins=20, density=False, range=(0., 1.))
        histograms[k] = hist
        bins[k] = bin_edges
    
    width = 0.7 * (bins[0][1] - bins[0][0])
    center = (bins[0][:-1] + bins[0][1:]) / 2
    
    cmap = plt.get_cmap('tab10')
    ylim = max([max(v) for v in histograms.values()])

    plt.figure(figsize=(15, 10))
        
    for i, k in enumerate(centralities.keys()):
        plt.subplot(2, 2, i + 1)  
        plt.xticks(bin_edges[::2])
        plt.bar(center, histograms[k], width=width, color=cmap.colors[i])
        plt.ylim((0, ylim + 10))
        plt.xlabel('centrality')
        plt.title(f'Time {k:02d}:00')
        plt.grid(axis='y')

    plt.suptitle(f'{metric.capitalize()} distributions for the temporal graph')
    plt.show()

    cumsums = dict()
    bins = dict()

    for k, v in centralities.items():
        hist, bin_edges = np.histogram(list(v.values()), bins=20, density=True, range=(0., 1.))
        cumsums[k] = np.cumsum(hist) * (bin_edges[1] - bin_edges[0])
        bins[k] = bin_edges
    center = (bins[0][:-1] + bins[0][1:]) / 2

    # Cumulative distribution
    plt.figure(figsize=(15, 5))
    plt.xticks(bin_edges[::2])
    for k, v in cumsums.items():
        plt.plot(center, v, 'o-', label=f'Time {k:2d}:00')
    plt.suptitle(f'{metric.capitalize()} cumulative distributions for the temporal graph')
    plt.xlabel('centrality')
    plt.grid(axis='y')
    plt.legend(loc='lower center', ncol=len(cumsums), bbox_to_anchor=(.5, -.25),
          columnspacing=8.5)
    plt.show()

def plot_spatial_network_centrality_distribution(centralities: Dict[str, float], metric: str):
    """Plot the centrality distibution and the cumulative centrality distribution in the spatial network.

    Parameters
    ----------
    centralities : Dict[str, float]
        Dictionary that for each node (key) contains its centrality (value)
    metric : str
        The name of the centrality metric.
    """
    hist, bin_edges = np.histogram(list(centralities.values()), bins=20, density=False, range=(0., 1.))

    width = 0.7 * (bin_edges[1] - bin_edges[0])
    center = (bin_edges[:-1] + bin_edges[1:]) / 2

    cmap = plt.get_cmap('tab10')

    plt.figure(figsize=(15, 5))

    plt.subplot(1, 2, 1)  
    plt.xticks(bin_edges[::2])
    plt.bar(center, hist, width=width, color=cmap.colors[0])
    plt.xlabel('centrality')
    plt.title(f'{metric.capitalize()} distribution for the spatial network ')
    plt.grid(axis='y')

    hist, bin_edges = np.histogram(list(centralities.values()), bins=20, density=True, range=(0., 1.))
    cumsum = np.cumsum(hist) * (bin_edges[1] - bin_edges[0])
    center = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Cumulative distribution
    plt.subplot(1, 2, 2) 
    plt.xticks(bin_edges[::2])
    plt.plot(center, cumsum, 'o-')
    plt.title(f'{metric.capitalize()} cumulative distribution for the spatial network')
    plt.xlabel('centrality')
    plt.grid(axis='y')
    plt.show()

_COMMUNITY_ALGORITHMS = ['Girvan-Newman', 'k-cores', 'Clique Percolation', 'Louvain']

def plot_temporal_network_modularities(undirected_temporal_networks_dict: Dict[int, nx.Graph], city_name: str,
                                       temporal_networks_girvan_newman_communities: Dict[int, Dict[str, int]],
                                       temporal_networks_k_core_communities: Dict[int, Dict[str, int]],
                                       temporal_networks_clique_percolation_communities: Dict[int, Dict[str, int]],
                                       temporal_networks_louvain_communities: Dict[int, Dict[str, int]]) -> None:
    """Compute and plot the modularity scores of each community detection algorithm on the undirected temporal network at different hours.

    Parameters
    ----------
    undirected_temporal_networks_dict : { int: Graph }
        Dictionary of undirected temporal networks.
    city_name : str
        The city name.
    temporal_networks_girvan_newman_communities : { int: { str: int } }
        Dictionary of the community detection results of Girvan-Newmann.
    temporal_networks_k_core_communities : { int: { str: int } }
        Dictionary of the community detection results of k-cores.
    temporal_networks_clique_percolation_communities : { int: { str: int } }
        Dictionary of the community detection results of Clique Percolation.
    temporal_networks_louvain_communities : { int: { str: int } }
        Dictionary of the community detection results of Louvain.
    """
    modularity_scores_temporal = { n: [] for n in _COMMUNITY_ALGORITHMS }

    for k, v in  undirected_temporal_networks_dict.items():
        modularity_scores_temporal['Girvan-Newman'].append(
            get_modularity_score(v,temporal_networks_girvan_newman_communities[k], weight='mean_travel_time'))
        modularity_scores_temporal['k-cores'].append(
            get_modularity_score(v, temporal_networks_k_core_communities[k], weight='mean_travel_time'))
        modularity_scores_temporal['Clique Percolation'].append(
            get_modularity_score(v, temporal_networks_clique_percolation_communities[k], weight='mean_travel_time'))
        modularity_scores_temporal['Louvain'].append(
            get_modularity_score(v, temporal_networks_louvain_communities[k], weight='mean_travel_time'))

    labels = [f'Temporal network at\ntime {k:02d}:00' for k in undirected_temporal_networks_dict.keys()]

    cmap = plt.get_cmap('tab10')

    x = np.arange(len(labels))
    width = 0.18
    fig, ax = plt.subplots(figsize=(15, 5))

    for i, (k, v) in enumerate(modularity_scores_temporal.items()):
        if i == 0:
                ax.bar(x - width * 1.5, v, width, label=k, color=cmap.colors[0])
                for x_, v_ in zip(x, v):
                    ax.text(x_ - .08 - width * 1.5, v_ + .002, f'{v_:.2f}', color='black', fontweight='bold')
        elif i == 1:
                ax.bar(x - width / 2, v, width, label=k, color=cmap.colors[1])
                for x_, v_ in zip(x, v):
                    ax.text(x_ - .08 - width / 2, v_ + .002, f'{v_:.2f}', color='black', fontweight='bold')
        elif i == 2:
                ax.bar(x + width / 2, v, width, label=k, color=cmap.colors[2])
                for x_, v_ in zip(x, v):
                    ax.text(x_ - .08 + width / 2, v_ + .002, f'{v_:.2f}', color='black', fontweight='bold')
        else:
                ax.bar(x + width * 1.5, v, width, label=k, color=cmap.colors[3])
                for x_, v_ in zip(x, v):
                    ax.text(x_ - .08 + width * 1.5, v_ + .002, f'{v_:.2f}', color='black', fontweight='bold')

    ax.set_ylabel('modularity')
    ax.set_title(f'Modularity scores for the temporal network of {city_name}')
    ax.set_xticks(x, labels)
    ax.legend(loc='lower center', ncol=len(modularity_scores_temporal), bbox_to_anchor=(.5, -.25),
            columnspacing=8.5)

    fig.tight_layout()

    plt.grid(axis='y')

    plt.show()

def plot_spatial_network_modularities(spatial_network: nx.Graph, city_name: str,
                                      spatial_network_girvan_newman_communities: Dict[str, int],
                                      spatial_network_k_core_communities: Dict[str, int],
                                      spatial_network_clique_percolation_communities: Dict[str, int],
                                      spatial_network_louvain_communities: Dict[str, int]) -> None:
    """Compute and plot the modularity scores of each community detection algorithm on the spatial network.

    Parameters
    ----------
    spatial_network : Graph
        The spatial network.
    city_name : str
        The city name.
    spatial_network_girvan_newman_communities : { int: { str: int } }
        Dictionary of the community detection results of Girvan-Newmann.
    spatial_network_k_core_communities : { int: { str: int } }
        Dictionary of the community detection results of k-cores.
    spatial_network_clique_percolation_communities : { int: { str: int } }
        Dictionary of the community detection results of Clique Percolation.
    spatial_network_louvain_communities : { int: { str: int } }
        Dictionary of the community detection results of Louvain.
    """
    modularities = [
        get_modularity_score(spatial_network, spatial_network_girvan_newman_communities, weight='weight'),
        get_modularity_score(spatial_network, spatial_network_k_core_communities, weight='weight'),
        get_modularity_score(spatial_network, spatial_network_clique_percolation_communities, weight='weight'),
        get_modularity_score(spatial_network, spatial_network_louvain_communities, weight='weight')
        ]

    x = np.arange(len(_COMMUNITY_ALGORITHMS))
    width = 0.4
    fig, ax = plt.subplots(figsize=(15, 5))

    cmap = plt.get_cmap('tab10')
    ax.bar(x, modularities, width, color=cmap.colors[:len(x)])

    for position, score in zip(x, modularities):
        ax.text(position - .06, score + .005, f'{score:.2f}', color='black', fontweight='bold')

    ax.set_ylabel('modularity')
    ax.set_title(f'Modularity scores for the spatial network of {city_name}')
    ax.set_xticks(x, _COMMUNITY_ALGORITHMS)

    fig.tight_layout()

    plt.grid(axis='y')

    plt.show()
