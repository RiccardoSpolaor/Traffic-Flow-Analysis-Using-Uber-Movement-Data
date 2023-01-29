import networkx as nx
from typing import Dict, Optional

_METRICS = ['in-deg', 'out-deg']

def get_metric(network: nx.Graph, metric: str, normalize: bool = True, weight: Optional[str] = None) -> Dict[int, float]:
    assert metric in _METRICS, f'Please, use one of the followng metrics: {"; ".join(_METRICS)}'

    if metric == 'in-deg':
        metric_dict = { n: network.in_degree(n, weight=weight) for n in network.nodes() }
    elif metric == 'out-deg':
        metric_dict = { n: network.out_degree(n, weight=weight) for n in network.nodes() }
    else:
        raise Exception('Metric not found')

    if normalize:
        return { n: v / max(metric_dict.values()) for n, v in metric_dict.items() }
    else:
        return metric_dict
