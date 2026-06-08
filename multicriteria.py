import networkx as nx
from graph_loader import time_cost, distance_cost, money_cost

def weighted_cost(attrs, a=1.0,b=0.0,c=0.0):
    return a*time_cost(attrs) + b*(distance_cost(attrs)/1000.0) + c*money_cost(attrs)

def route_weighted(G, src, dst, a=1.0,b=0.2,c=5.0):
    w=lambda u,v,attrs: weighted_cost(attrs,a,b,c)
    return nx.shortest_path(G, src, dst, weight=w)

def k_shortest_paths(G, src, dst, k=5, weight_fn=lambda u,v,attrs: time_cost(attrs)):
    return list(nx.shortest_simple_paths(G, src, dst, weight=weight_fn))[:k]

def pareto_routes(G, src, dst, k=8):
    routes = k_shortest_paths(G, src, dst, k=k, weight_fn=lambda u,v,attrs: time_cost(attrs))
    scored=[]
    for p in routes:
        t=sum(time_cost(G[u][v]) for u,v in zip(p[:-1],p[1:]))
        d=sum(distance_cost(G[u][v]) for u,v in zip(p[:-1],p[1:]))
        m=sum(money_cost(G[u][v]) for u,v in zip(p[:-1],p[1:]))
        scored.append((p,(t,d,m)))
    # Pareto filter
    pareto=[]
    for p,vec in scored:
        if not any((q!=p and all(vq<=v for vq,v in zip(vecq,vec)) and any(vq<v for vq,v in zip(vecq,vec)))
                   for q,vecq in scored):
            pareto.append((p,vec))
    return pareto

