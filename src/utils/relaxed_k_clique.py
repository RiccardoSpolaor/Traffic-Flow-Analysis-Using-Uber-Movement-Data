import networkx as nx
from copy import deepcopy

from typing import Set, List

'''def _get_longest_path_value(G: nx.Graph, S: Set, weight: str):
    G_sub = nx.subgraph(G, S)
    paths = []
    for u in S:
        paths += list(nx.all_simple_paths(G_sub, u, S - {u}, cutoff=None))
    
    longest_path_value = 0
    for p in paths:
        path_length = 0
        for u, v in zip(p[:], p[1:]):
            path_length += G_sub[u][v][weight]
        longest_path_value = max([longest_path_value, path_length])
        
    print(longest_path_value)

    return longest_path_value''';

def _get_longest_path_value(G: nx.Graph, S: Set, weight: str):
    G_sub = nx.subgraph(G, S)
    G_neg = deepcopy(G_sub)
    
    for u, v, d in G_sub.edges():
        G_neg[u][v][weight] = d[weight]
        
    longest_paths_negative_lengths = list(nx.shortest_path_length(G_neg, weight=weight, method='dijkstra'))
    
    longest_path_length = - min([p for paths_of_node in longest_paths_negative_lengths for p in paths_of_node[1].values()])
        
    print(longest_path_length)

    return longest_path_length

def get_k_clubs(G: nx.Graph, k: int, weight: str):
    k_clubs = []
    for u in G.nodes():
        _iterate_k_clubs(G, {u}, k, weight, k_clubs)
    return k_clubs

def _iterate_k_clubs(G: nx.Graph, S: Set, k: int, weight: str, k_clubs: List[List]):
    if _get_longest_path_value(G, S, weight) <= k:
        flag = False
        for v in S:
            for w in set(nx.all_neighbors(G, v)) - S:
                new_S = S.add(w)
                if _get_longest_path_value(G, S, weight) <= k:
                    flag = True
                    _iterate_k_clubs(G, new_S, k, weight)
        if flag == False:
            k_clubs.append(S)
