from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from graph_loader import load_graph, time_cost
from router import shortest_path, path_cost
from multicriteria import route_weighted, pareto_routes
from dynamics import apply_traffic, close_road

app = FastAPI(title="Intelligent Route Planner")

# ---------------------------
# CORS CONFIGURATION
# ---------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# LOAD GRAPH
# ---------------------------

G = load_graph("roads.csv")

# ---------------------------
# REQUEST MODEL
# ---------------------------

class RouteReq(BaseModel):
    src: str
    dst: str

    objective: str = "time"

    alpha: float = 1.0
    beta: float = 0.2
    gamma: float = 5.0

    traffic_edges: list[tuple[str, str]] = []
    close_edges: list[tuple[str, str]] = []

# ---------------------------
# HOME ROUTE
# ---------------------------

@app.get("/")
def home():
    return {
        "message": "Intelligent Route Planner API Running"
    }

# ---------------------------
# GEOJSON CONVERTER
# ---------------------------

def path_to_geojson(graph, path):

    coords = []

    for u, v in zip(path[:-1], path[1:]):

        edge = graph[u][v]

        coords.append([
            edge["lon_u"],
            edge["lat_u"]
        ])

    last = graph[path[-2]][path[-1]]

    coords.append([
        last["lon_v"],
        last["lat_v"]
    ])

    return {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": coords
        }
    }

# ---------------------------
# ROUTE API
# ---------------------------

@app.post("/route")
def route(req: RouteReq):

    H = G.copy()

    # Apply traffic
    for uv in req.traffic_edges:

        apply_traffic(
            H,
            where=lambda u, v, a, uv=tuple(uv):
            (u, v) == tuple(uv),
            factor=1.5
        )

    # Close roads
    for uv in req.close_edges:

        try:
            close_road(H, tuple(uv))
        except Exception:
            pass

    # Route selection
    if req.objective == "weighted":

        path = route_weighted(
            H,
            req.src,
            req.dst,
            req.alpha,
            req.beta,
            req.gamma
        )

    else:

        path = shortest_path(
            H,
            req.src,
            req.dst,
            req.objective
        )

    total_time = path_cost(
        H,
        path,
        time_cost
    )

    geojson = path_to_geojson(
        H,
        path
    )

    return {
        "path": path,
        "eta_sec": round(total_time, 1),
        "geojson": geojson
    }

# ---------------------------
# ALTERNATIVE ROUTES API
# ---------------------------

@app.get("/alternatives")
def alternatives(
    src: str,
    dst: str,
    k: int = 5
):

    routes = pareto_routes(
        G,
        src,
        dst,
        k=k
    )

    return [
        {
            "path": path,
            "time_sec": round(time_val, 1),
            "dist_m": round(dist_val, 1),
            "tolls": int(tolls)
        }
        for path, (time_val, dist_val, tolls)
        in routes
    ]