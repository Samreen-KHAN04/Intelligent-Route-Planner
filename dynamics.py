def apply_traffic(G, where=lambda u,v,attrs: True, factor=1.2):
    for u,v,attrs in G.edges(data=True):
        if where(u,v,attrs): attrs["traffic_factor"]=factor

def close_road(G, edge_uv): 
    if G.has_edge(*edge_uv): G.remove_edge(*edge_uv)

def route_with_turn_penalties(G, src, dst, base_cost_fn, turn_penalty_sec=10):
    import heapq
    # state is (cost, node, prev_node)
    pq=[(0, src, None)]; seen={}
    parent={}
    while pq:
        c,n,prev=heapq.heappop(pq)
        key=(n,prev)
        if key in seen and c>=seen[key]: continue
        seen[key]=c
        if n==dst:
            # reconstruct path using parent keyed by (node, prev)
            path=[n]; cur=(n,prev)
            while cur in parent:
                n2,prev2=parent[cur]
                path.append(n2); cur=(n2,prev2)
            return list(reversed(path))
        for _,v,attrs in G.out_edges(n, data=True):
            base = base_cost_fn(attrs)
            turn = 0
            if prev is not None and prev!=n:
                # simple turn penalty when changing direction (approx)
                turn = turn_penalty_sec
            heapq.heappush(pq, (c+base+turn, v, n))
            parent[(v,n)] = (n,prev)
    raise ValueError("No path")
