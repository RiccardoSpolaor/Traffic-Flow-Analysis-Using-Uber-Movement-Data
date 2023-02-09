import geopandas as gpd
import networkx as nx
from shapely.validation import make_valid
from sklearn.metrics.pairwise import haversine_distances
from typing import Dict


def _get_spatial_network_adjacency_dict(gdf: gpd.GeoDataFrame) -> Dict[int, Dict[str, float]]:
    """Get the spatial network adjacency dictionary.

    Parameters
    ----------
    gdf : GeoDataFrame
        The geodataframe used to build the adjacency dictionary.

    Returns
    -------
    Dict[int, Dict[str, float]]
        The adjacency dictionary (key: ID, value: {'weight': float}).
    """
    adjacency_dict = dict()
    
    gdf.geometry = gdf.geometry.apply(lambda x: make_valid(x))

    for row in gdf.itertuples(index=False):
        # Get the row ID and centroid
        row_id, row_centroid = row.MOVEMENT_ID, row.centroid

        # Get "not-disjoint" locations to the current row (i.e.: the neighbor locations)
        neighbors = gdf[(~gdf.geometry.disjoint(row.geometry)) & (gdf.MOVEMENT_ID != row_id)]

        # Get the neighbor IDs and centroids
        neighbor_ids, neighbor_centroids = neighbors.MOVEMENT_ID.tolist(), neighbors.centroid.tolist()

        # Compute haversine distances between each neighbour centroid and the row centroid
        distances = [haversine_distances([[row_centroid.x, row_centroid.y], [c.x, c.y]])[0,1] for c in neighbor_centroids]

        # Add adjacency dict entry for the current row based on its ID
        adjacency_dict[row_id] = { n: {'weight': d } for n, d in zip(neighbor_ids, distances) }
        
    return adjacency_dict

def get_spatial_network(gdf: gpd.GeoDataFrame) -> nx.Graph:
    """Get the spatial network from a geodataframe.

    Parameters
    ----------
    gdf : GeoDataFrame
        The geodataframe used to get the spatial network.

    Returns
    -------
    Graph
        The spatial network.
    """
    # Get adjacecy dictionary
    adjacency_dict = _get_spatial_network_adjacency_dict(gdf)

    # Get the spatial network
    spatial_network = nx.from_dict_of_dicts(adjacency_dict)
    return spatial_network
