import itertools
import networkx as nx
from typing import Dict, Optional

_CENTRALITY_METRICS = ['in-deg', 'out-deg', 'betweenness', 'closeness', 'pagerank', 'hits']

def get_nodes_centrality(network: nx.Graph, metric: str, normalize: bool = True,
                         weight: Optional[str] = None) -> Dict[int, float]:
    assert metric in _CENTRALITY_METRICS, f'Please, use one of the followng metrics: {"; ".join(_CENTRALITY_METRICS)}'

    if metric == 'in-deg':
        metric_dict = { n: network.in_degree(n, weight=weight) for n in network.nodes() }
    elif metric == 'out-deg':
        metric_dict = { n: network.out_degree(n, weight=weight) for n in network.nodes() }
    elif metric == 'betweenness':
        metric_dict = nx.betweenness_centrality(network, k=None, normalized=normalize, weight=weight, endpoints=False, 
                                                seed=42)
        return metric_dict
    elif metric == 'closeness':
        metric_dict = nx.closeness_centrality(network, u=None, distance=weight)
        return metric_dict
    elif metric == 'pagerank':
        metric_dict = nx.pagerank(network, alpha=0.85, max_iter=100, tol=1e-06, nstart=None, weight=weight, dangling=None)
    elif metric == 'hits':
        metric_dict = nx.hits(network, max_iter=100, tol=1e-08, nstart=None, normalized=normalize)
        return metric_dict
    else:
        raise Exception('Metric not found')

    if normalize:
        return { n: v / max(metric_dict.values()) for n, v in metric_dict.items() }
    else:
        return metric_dict

_COMMUNITY_METRICS = ['girvan-newman', 'k-core']

def get_nodes_community(network: nx.Graph, metric: str, weight: Optional[str] = None, k: int = 2) -> Dict[int, int]:
    assert metric in _COMMUNITY_METRICS, f'Please, use one of the followng metrics: {"; ".join(_COMMUNITY_METRICS)}'
    
    def most_central_edge(network: nx.Graph):
        centrality = nx.edge_betweenness_centrality(network, weight=weight)
        return max(centrality, key=centrality.get)

    if metric == 'girvan-newman':
        communities_iterator = nx.community.girvan_newman(network, most_valuable_edge=most_central_edge)
        
        for _ in range(k - 1):
            communities = next(communities_iterator)
        
        #limited = itertools.takewhile(lambda c: len(c) <= k, communities_iterator)
        #for communities in limited:
        #    print(tuple(sorted(c) for c in communities))
        #*_, last = limited
        return { c: i for i, community in enumerate(communities) for c in community }
    else:
        raise Exception('Metric not found')
