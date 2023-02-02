import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import cm, colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
import networkx as nx
from typing import Dict

from utils.geodataframe import get_geodataframe_coordinates_dict

def plot_spatial_network(gdf: gpd.GeoDataFrame, spatial_network: nx.Graph, title: str = 'Spatial network') -> None:
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

def plot_centrality(gdf: gpd.GeoDataFrame, spatial_network: nx.Graph, metric_dictionary: Dict[int, str],
                title: str = 'Metric plot', cmap: colors.LinearSegmentedColormap = plt.cm.YlGnBu) -> None:
    fig, ax = plt.subplots(1, figsize=(15, 10))

    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='2%', pad=-.0005)

    gdf.plot(ax=ax, edgecolor='darkgray', color='lightgray')

    coordinates = get_geodataframe_coordinates_dict(gdf)
    node_colors = [metric_dictionary[n] if n in metric_dictionary.keys() else None for n in spatial_network.nodes()]

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
        cmap=cmap
    )

    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    norm = colors.Normalize(vmin=0., vmax=1.)
    fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap),
                cax=cax)

    ax.set_title(title)

    plt.show()

def plot_communities(gdf: gpd.GeoDataFrame, spatial_network: nx.Graph, metric_dictionary: Dict[int, str],
                     title: str = 'Metric plot', cmap: colors.ListedColormap = plt.cm.tab10) -> None:
    _, ax = plt.subplots(1, figsize=(15, 10))

    #divider = make_axes_locatable(ax)
    #cax = divider.append_axes('right', size='2%', pad=-.0005)

    gdf.plot(ax=ax, edgecolor='darkgray', color='lightgray')

    coordinates = get_geodataframe_coordinates_dict(gdf)
    node_colors = [metric_dictionary[n] if n in metric_dictionary.keys() else None for n in spatial_network.nodes()]

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
        #cmap=cmap
    )

    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    #norm = colors.Normalize(vmin=0., vmax=1.)
    #fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap),
    #            cax=cax)

    ax.set_title(title)

    plt.show()