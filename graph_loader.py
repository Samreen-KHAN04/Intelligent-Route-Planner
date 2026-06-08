import csv, math
import networkx as nx

def load_graph(csv_path="roads.csv"):
    G = nx.DiGraph()
    with open(csv_path, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            u, v = row["u"], row["v"]
            attrs = {
                "lat_u": float(row["lat_u"]), "lon_u": float(row["lon_u"]),
                "lat_v": float(row["lat_v"]), "lon_v": float(row["lon_v"]),
                "distance_m": float(row["distance_m"]),
                "speed_kph": float(row["speed_kph"]),
                "toll": int(row["toll"]),
                "one_way": int(row["one_way"]),
                "road_class": row["road_class"],
                "traffic_factor": 1.0
            }
            base_sec = attrs["distance_m"] / (attrs["speed_kph"]*1000/3600)
            attrs["base_sec"] = base_sec
            G.add_edge(u, v, **attrs)
    return G

def time_cost(e): return e["base_sec"] * e.get("traffic_factor",1.0)
def distance_cost(e): return e["distance_m"]
def money_cost(e): return e["toll"]  # simple: count toll gates
def eco_cost(e):  # proxy: time * class factor (primary roads penalized less)
    cls = e["road_class"]; f = 0.9 if cls=="primary" else 1.0
    return time_cost(e)*f
