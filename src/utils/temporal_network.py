import networkx as nx
import pandas as pd
from typing import Dict, List

class TemporalNetwork(nx.DiGraph):
    """ 
    Class representing a temporal directed network.
    The class inherits from `DiGraph` and overrides the `to_undirected` method.
    """
    def __init__(self) -> None:
        super().__init__()
        
    def to_undirected(self) -> nx.Graph:
        """Function to turn the network from directed to undirected
        Resulting edges weights are obtained as the sum of the directed edges from u to v or v to u divided by their quantity.

        Returns
        -------
        Graph
            The undirected version of the original graph
        """
        undirected_network = nx.Graph()
        
        undirected_network.add_nodes_from(self.nodes)

        undirected_network.add_edges_from(self.edges(), mean_travel_time=0)

        for u, v, d in self.edges(data=True):
            undirected_network[u][v]['mean_travel_time'] += d['mean_travel_time']
            
        for u, v in undirected_network.edges():
            if self.has_edge(u, v) and self.has_edge(v, u):
                undirected_network[u][v]['mean_travel_time'] /= 2
                
        return undirected_network

def get_movement_dataframe(csv_path: str) -> pd.DataFrame:
    """Function to obtain a pandas dataframe from the Uber Movement data.

    Parameters
    ----------
    csv_path : str
        Path of the csv file containing the Uber Movement data.

    Returns
    -------
    DataFrame
        The data converted in pandas dataframe.
    """
    df = pd.read_csv(csv_path)
    df.drop(['standard_deviation_travel_time', 'geometric_mean_travel_time', 'geometric_standard_deviation_travel_time'],
            inplace=True, axis=1)
    
    df['sourceid'] = df['sourceid'].apply(str)
    df['dstid'] = df['dstid'].apply(str)
    
    return df

def get_temporal_networks_from_pandas_edgelist(df: pd.DataFrame, hours: List[int]) -> Dict[int, TemporalNetwork]:
    """Function to build the dictionary of temporal networks at a specific hour from a pandas dataframe containing the edge data.

    Parameters
    ----------
    df : DataFrame
        The pandas dataframe containing the edge data.
    hours : List[int]
        List of hours to consider to build the dictionary of temporal networks.

    Returns
    -------
    { int: TemporalNetwork }
        Dictionary of temporal networks (values) at a specific hour (keys).
    """
    return {
        h: nx.from_pandas_edgelist(
            df[df.hod == h],
            source='sourceid',
            target='dstid',
            edge_attr='mean_travel_time',
            create_using=TemporalNetwork())
        for h in hours
    }
