import networkx as nx
from typing import Dict, Optional

_METRICS = ['in-deg', 'out-deg', 'betweenness', 'closeness', 'pagerank', 'hits']

def get_metric(network: nx.Graph, metric: str, normalize: bool = True, weight: Optional[str] = None) -> Dict[int, float]:
    assert metric in _METRICS, f'Please, use one of the followng metrics: {"; ".join(_METRICS)}'

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
