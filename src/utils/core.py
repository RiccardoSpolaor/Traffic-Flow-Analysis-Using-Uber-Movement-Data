"""
Edited from the Networkx Documentation

Find the k-cores of a graph.

The k-core is found by recursively pruning nodes with degrees less than k.

See the following references for details:

An O(m) Algorithm for Cores Decomposition of Networks
Vladimir Batagelj and Matjaz Zaversnik, 2003.
https://arxiv.org/abs/cs.DS/0310049

Generalized Cores
Vladimir Batagelj and Matjaz Zaversnik, 2002.
https://arxiv.org/pdf/cs/0202039

For directed graphs a more general notion is that of D-cores which
looks at (k, l) restrictions on (in, out) degree. The (k, k) D-core
is the k-core.

D-cores: Measuring Collaboration of Directed Graphs Based on Degeneracy
Christos Giatsidis, Dimitrios M. Thilikos, Michalis Vazirgiannis, ICDM 2011.
http://www.graphdegeneracy.org/dcores_ICDM_2011.pdf

Multi-scale structure and topological anomaly detection via a new network \
statistic: The onion decomposition
L. Hébert-Dufresne, J. A. Grochow, and A. Allard
Scientific Reports 6, 31708 (2016)
http://doi.org/10.1038/srep31708

Edits list:
- Addition of types
- Addition of extra parameters or controls in some functions to allow the use of weights
- Function `core_number_weighted` created from scratch.

"""
import networkx as nx
from networkx.exception import NetworkXError
from networkx.utils import not_implemented_for
from typing import Callable, Dict, Optional

def core_number_weighted(network: nx.Graph, weight: str) -> Dict[str, float]:
    """Get the weighted core number of each node in the network

    Parameters
    ----------
    network : Graph
        The mnetwork from which the core numbers are obtained
    weight : str
        The name of the weight on the edges that has to be used to compute the weighted core number of the nodes

    Returns
    -------
    { str: float }
        Dictionary containing for each node its weighted core number
    """
    # Get weighted node degree dictionary.
    degrees = dict(network.degree(weight=weight))
    # Sort nodes by non-decreasing degree.
    nodes = sorted(degrees, key=degrees.get)

    # Initialize core_number dictionary
    cores = {k: 0 for k in nodes}

    for i in range(len(nodes)):
        # Get current node
        u = nodes[i]
        # Initialize its core value as its degree
        cores[u] = degrees[u]
        # Update neighbouring nodes core number
        for w in list(nx.all_neighbors(network, u)):
            if cores[u] < degrees[w]:
                degrees[w] = max(degrees[w] - network[u][w][weight], cores[u])
        nodes[i+1:] = sorted({k: v for k, v in degrees.items() if k in nodes[i+1:]}, key=degrees.get)

    return cores
    

#@nx._dispatch
@not_implemented_for("multigraph")
def core_number(G: nx.Graph):
    """Returns the core number for each vertex.

    A k-core is a maximal subgraph that contains nodes of degree k or more.

    The core number of a node is the largest value k of a k-core containing
    that node.

    Parameters
    ----------
    G : NetworkX graph
       A graph or directed graph

    Returns
    -------
    core_number : dictionary
       A dictionary keyed by node to the core number.

    Raises
    ------
    NetworkXError
        The k-core is not implemented for graphs with self loops
        or parallel edges.

    Notes
    -----
    Not implemented for graphs with parallel edges or self loops.

    For directed graphs the node degree is defined to be the
    in-degree + out-degree.

    References
    ----------
    .. [1] An O(m) Algorithm for Cores Decomposition of Networks
       Vladimir Batagelj and Matjaz Zaversnik, 2003.
       https://arxiv.org/abs/cs.DS/0310049
    """
    if nx.number_of_selfloops(G) > 0:
        msg = (
            "Input graph has self loops which is not permitted; "
            "Consider using G.remove_edges_from(nx.selfloop_edges(G))."
        )
        raise NetworkXError(msg)
    degrees = dict(G.degree())
    # Sort nodes by degree.
    nodes = sorted(degrees, key=degrees.get)
    bin_boundaries = [0]
    curr_degree = 0
    for i, v in enumerate(nodes):
        if degrees[v] > curr_degree:
            bin_boundaries.extend([i] * (degrees[v] - curr_degree))
            curr_degree = degrees[v]
    node_pos = {v: pos for pos, v in enumerate(nodes)}
    # The initial guess for the core number of a node is its degree.
    core = degrees
    nbrs = {v: list(nx.all_neighbors(G, v)) for v in G}
    for v in nodes:
        for u in nbrs[v]:
            if core[u] > core[v]:
                nbrs[u].remove(v)
                pos = node_pos[u]
                bin_start = bin_boundaries[core[u]]
                node_pos[u] = bin_start
                node_pos[nodes[bin_start]] = pos
                nodes[bin_start], nodes[pos] = nodes[pos], nodes[bin_start]
                bin_boundaries[core[u]] += 1
                core[u] -= 1
    return core



def _core_subgraph(G: nx.Graph, k_filter: Callable[[float, float, Dict[str, float]],bool], k: Optional[float] = None,
                   core: Optional[Dict[str, float]] = None, weight: Optional[str] = None) -> nx.Graph:
    """Returns the subgraph induced by nodes passing filter `k_filter`.

    Parameters
    ----------
    G : NetworkX graph
       The graph or directed graph to process
    k_filter : filter function
       This function filters the nodes chosen. It takes three inputs:
       A node of G, the filter's cutoff, and the core dict of the graph.
       The function should return a Boolean value.
    k : int, optional
      The order of the core. If not specified use the max core number.
      This value is used as the cutoff for the filter.
    core : dict, optional
      Precomputed core numbers keyed by node for the graph `G`.
      If not specified, the core numbers will be computed from `G`.
    weight : str, optional
      The name of the weight on the edges that has to be used to compute the weighted core number of the nodes
    """
    if core is None:
        if weight is None:
          core = core_number(G)
        else:
          core = core_number_weighted(G, weight)
    if k is None:
        k = sum(core.values()) / len(core)
    nodes = (v for v in core if k_filter(v, k, core))
    return G.subgraph(nodes).copy()

def k_core(G: nx.Graph, k: Optional[float] =None, core_number: Optional[Optional[Dict[str, float]]] = None, 
           weight: Optional[str] = None) -> nx.Graph:
    """Returns the k-core of G.

    A k-core is a maximal subgraph that contains nodes of degree k or more.

    Parameters
    ----------
    G : NetworkX graph
      A graph or directed graph
    k : int, optional
      The order of the core.  If not specified return the main core.
    core_number : dictionary, optional
      Precomputed core numbers for the graph G.
    weight : str, optional
      The weight used to compute the k-core

    Returns
    -------
    G : NetworkX graph
      The k-core subgraph

    Raises
    ------
    NetworkXError
      The k-core is not defined for graphs with self loops or parallel edges.

    Notes
    -----
    The main core is the core with the largest degree.

    Not implemented for graphs with parallel edges or self loops.

    For directed graphs the node degree is defined to be the
    in-degree + out-degree.

    Graph, node, and edge attributes are copied to the subgraph.

    See Also
    --------
    core_number

    References
    ----------
    .. [1] An O(m) Algorithm for Cores Decomposition of Networks
       Vladimir Batagelj and Matjaz Zaversnik,  2003.
       https://arxiv.org/abs/cs.DS/0310049
    """

    def k_filter(v, k, c):
        return c[v] >= k

    return _core_subgraph(G, k_filter, k, core_number, weight)