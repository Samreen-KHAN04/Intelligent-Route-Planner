import networkx as nx, math
from graph_loader import load_graph, time_cost, distance_cost, money_cost, eco_cost

def path_cost(G, path, cost_fn):
    return sum(cost_fn(G[u][v]) for u,v in zip(path[:-1], path[1:]))

def weight_factory(cost_fn):
    def w(u,v,attrs): return cost_fn(attrs)
    return w

def haversine_m(lat1,lon1,lat2,lon2):
    R=6371000
    from math import radians,sin,cos,asin,sqrt
    dlat=radians(lat2-lat1); dlon=radians(lon2-lon1)
    a=sin(dlat/2)**2+cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 2*R*asin(sqrt(a))

def astar_heuristic(G, n1, n2):
    # optimistic time heuristic based on straight-line distance at 80 km/h
    lat1,lon1 = G.edges[list(G.out_edges(n1))[0]]["lat_u"], G.edges[list(G.out_edges(n1))[0]]["lon_u"]
    lat2,lon2 = G.edges[list(G.out_edges(n2))[0]]["lat_u"], G.edges[list(G.out_edges(n2))[0]]["lon_u"]
    d = haversine_m(lat1,lon1,lat2,lon2)
    best_mps = 80_000/3600
    return d / best_mps

def shortest_path(G, src, dst, objective="time"):
    cost_map = {"time": time_cost, "distance": distance_cost, "money": money_cost, "eco": eco_cost}
    cfn = cost_map[objective]
    if objective=="time":
        # A* on time
        return nx.astar_path(G, src, dst, heuristic=lambda n1,n2: astar_heuristic(G,n1,n2), weight=weight_factory(cfn))
    else:
        return nx.shortest_path(G, src, dst, weight=weight_factory(cfn))
