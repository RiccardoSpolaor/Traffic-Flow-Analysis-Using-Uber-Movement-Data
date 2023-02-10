import networkx as nx

def weighted_k_truss(G: nx.Graph, k: int, w: float, weight: str):
    """
    Compute the weighted k-truss of a graph.
    """
    truss = nx.Graph()
    for u, v in G.edges():
        truss.add_edge(u, v, support=0)
    
    for node in G.nodes():
        neighbors = list(G.neighbors(node))
        for i in range(len(neighbors)):
            for j in range(i+1, len(neighbors)):
                u, v = neighbors[i], neighbors[j]
                if G.has_edge(u, v):
                  weight_ = G[node][u][weight] + G[node][v][weight]
                  if weight_ <= w:
                      truss[u][v]['support'] += 1
    
    result = nx.Graph()
    for edge in truss.edges():
        if truss[edge[0]][edge[1]]['support'] >= k-2:
            result.add_edge(edge[0], edge[1], weight=G[edge[0]][edge[1]][weight])
    
    return result
