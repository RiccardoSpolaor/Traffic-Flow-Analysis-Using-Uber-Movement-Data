import geopandas as gpd
import json
from shapely.geometry import shape
from typing import Dict, Tuple


def get_geodataframe(geojson_file_path: str) -> gpd.GeoDataFrame:
    """Get a geodataframe from a geojson file.

    Parameters
    ----------
    geojson_file_path : str
        The geojson file path.

    Returns
    -------
    GeoDataFrame
        The geodataframe based on the geojson.
    """
    with open(geojson_file_path) as f:
        # Load the geojson file and keep just the `features` field
        geo_json = json.load(f)
        geo_json = geo_json['features']

        for g in geo_json:
            # Overwrite the `geometry` field by computing the actual geometry shape from the geojson
            g['geometry'] = shape(g['geometry'])
            # Create a field for each subfield of `properties`
            for k, v in g['properties'].items():
                g[k] = v
            # Delete unuseful fields
            del g['properties']
            del g['type']

    # Create geopandas dataframe
    gdf = gpd.GeoDataFrame(geo_json)

    return gdf

def get_geodataframe_coordinates_dict(gdf: gpd.GeoDataFrame) -> Dict[int, Tuple[int, int]]:
    """Get the dictionary of the coordinates of the centroids of each element in the geodataframe.

    Parameters
    ----------
    gdf : GeoDataFrame
        The geodataframe from which the coordinates dictionary is built.

    Returns
    -------
    Dict[int, Tuple[int, int]]
        The coordinates dictionary.
    """
    coordinates = dict()
    for r in gdf.itertuples(index=False):
        coordinates[r.MOVEMENT_ID] = (r.centroid.x, r.centroid.y)
    return coordinates

def set_geodataframe_centroids(gdf: gpd.GeoDataFrame) -> None:
    """Set the centroid value of each entry in the geodataframe based on their geometry.

    Parameters
    ----------
    gdf : GeoDataFrame
        The geodataframe for which the centroids are set.
    """
    gdf['centroid'] = gdf.geometry.apply(lambda x: x.centroid)