import networkx as nx
import pandas as pd
from typing import Dict

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

        undirected_network.add_edges_from(self.edges(), mean_travel_time=0)

        for u, v, d in self.edges(data=True):
            undirected_network[u][v]['mean_travel_time'] += d['mean_travel_time']
            
        for u, v in undirected_network.edges():
            if self.has_edge(u, v) and self.has_edge(v, u):
                undirected_network[u][v]['mean_travel_time'] /= 2
                
        return undirected_network
    
def get_temporal_networks_from_pandas_edgelist(df: pd.DataFrame) -> Dict[int, TemporalNetwork]:
    return {
        h: nx.from_pandas_edgelist(
            df[df.hod == h],
            source='sourceid',
            target='dstid',
            edge_attr='mean_travel_time',
            create_using=TemporalNetwork())
        for h in range(24)
    }
