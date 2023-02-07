from copy import deepcopy
import networkx as nx
from typing import Dict, Optional

from utils.core import k_core
from utils.relaxed_k_clique import get_k_clubs
from utils.hits import weighted_hits
from utils.k_clique import k_clique_communities

_CENTRALITY_METRICS = ['in-deg', 'out-deg', 'betweenness', 'closeness', 'pagerank', 'hits']

def get_nodes_centrality(network: nx.Graph, metric: str, normalize: bool = True,
                         weight: Optional[str] = None) -> Dict[int, float]:
    assert metric in _CENTRALITY_METRICS, f'Please, use one of the followng metrics: {"; ".join(_CENTRALITY_METRICS)}'

    if metric == 'in-deg':
        metric_dict = { n: network.in_degree(n, weight=weight) for n in network.nodes() }
    elif metric == 'out-deg':
        metric_dict = { n: network.out_degree(n, weight=weight) for n in network.nodes() }
    elif metric == 'betweenness':
        metric_dict = nx.betweenness_centrality(network, k=None, normalized=False, weight=weight, endpoints=False, seed=42)
        #return metric_dict
    elif metric == 'closeness':
        metric_dict = nx.closeness_centrality(network, u=None, distance=weight)
        # return metric_dict
    elif metric == 'pagerank':
        metric_dict = nx.pagerank(network, alpha=0.85, max_iter=100, tol=1e-06, nstart=None, weight=weight, dangling=None)
    elif metric == 'hits':
        metric_dict = weighted_hits(network, normalized=normalize, weight=weight)
        return metric_dict
    else:
        raise Exception('Metric not found')

    if normalize:
        return { n: (v - min(metric_dict.values())) / (max(metric_dict.values()) - min(metric_dict.values())) 
                for n, v in metric_dict.items() }
    else:
        return metric_dict

def normalize_centrality_measures(centrality_dict: Dict[int, Dict[int, float]]) -> Dict[int, Dict[int, float]]:
    centrality_dict = deepcopy(centrality_dict)
    
    values_list = [v for centralities in centrality_dict.values() for v in centralities.values()]
    min_value = min(values_list)
    max_value = max(values_list)
    
    for centralities in centrality_dict.values():
        for k, v in centralities.items():
            centralities[k] = (v - min_value) / (max_value - min_value)

    return centrality_dict

def get_girvan_newman_communities(network: nx.Graph, weight: Optional[str] = None, k: int = 2) -> Dict[int, int]:
    def most_central_edge(network: nx.Graph):
        centrality = nx.edge_betweenness_centrality(network, weight=weight)
        return max(centrality, key=centrality.get)

    communities_iterator = nx.community.girvan_newman(network, most_valuable_edge=most_central_edge)
    
    for _ in range(k - 1):
        communities = next(communities_iterator)
    
    return { c: i for i, community in enumerate(communities) for c in community }

def get_k_cores_communities(network: nx.Graph, weight: Optional[str] = None, k: Optional[int] = None) -> Dict[int, int]:
    new_network = deepcopy(network)
    node_cores_dict = {}
    n = 0
    
    while len(new_network.nodes()):
        try:
            k_core_subgraph = k_core(new_network, k=k, weight=weight)
        except ValueError:
            break

        for node in k_core_subgraph.nodes():
            node_cores_dict[node] = n
            new_network.remove_node(node)
            
        n += 1

    for node in new_network.nodes():
        node_cores_dict[node] = n
    
    return node_cores_dict

def get_k_clique_communities(network: nx.Graph, k: int, l: float, weight: Optional[str] = None) -> Dict[int, int]:
    community_iterator = k_clique_communities(network, weight=weight, l=l, k=k)

    communities = dict()
    for i, clique in enumerate(list(community_iterator)):
        for c in clique:
            communities[c] = i

    return communities

def get_k_clubs_communities(network: nx.Graph, k: int, weight: str) -> Dict[int, int]:
    new_network = deepcopy(network)
    node_cores_dict = {}
    n = 0
    
    while len(new_network.nodes()):
        try:
            k_clubs = get_k_clubs(new_network, k=k, weight=weight)
        except ValueError:
            break

        for sub in k_clubs:
            for n in sub:
                node_cores_dict[node] = n
                new_network.remove_node(node)
        n += 1
        k /= 2

    for node in new_network.nodes():
        node_cores_dict[node] = n
    
    return node_cores_dict

