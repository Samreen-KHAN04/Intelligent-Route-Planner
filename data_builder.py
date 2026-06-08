import csv, math

def write_grid(n=5, spacing_m=300):
    rows=[]
    node_id=lambda i,j: f"N{i}_{j}"
    coords={}
    for i in range(n):
        for j in range(n):
            # fake lat/lon grid (not geo-accurate, fine for demo)
            lat, lon = 12.90 + i*0.002, 77.50 + j*0.002
            coords[node_id(i,j)] = (lat, lon)
    def add(u,v,dist,speed,toll,one_way,cls):
        lat_u,lon_u = coords[u]; lat_v,lon_v = coords[v]
        rows.append([u,v,lat_u,lon_u,lat_v,lon_v,dist,speed,toll,one_way,cls])

    for i in range(n):
        for j in range(n):
            if j+1<n:
                u=node_id(i,j); v=node_id(i,j+1)
                add(u,v,spacing_m,40,0,0,"residential")
                add(v,u,spacing_m,40,0,0,"residential")
            if i+1<n:
                u=node_id(i,j); v=node_id(i+1,j)
                add(u,v,spacing_m,35,0,0,"residential")
                add(v,u,spacing_m,35,0,0,"residential")

    # Add a faster avenue with toll across row 2
    for j in range(n-1):
        u=node_id(2,j); v=node_id(2,j+1)
        add(u,v,spacing_m,70,1,0,"primary")
        add(v,u,spacing_m,70,1,0,"primary")

    # A one-way shortcut
    add(node_id(0,0), node_id(1,1), spacing_m*1.4, 50, 0, 1, "link")

    with open("roads.csv","w",newline="") as f:
        w=csv.writer(f)
        w.writerow("u,v,lat_u,lon_u,lat_v,lon_v,distance_m,speed_kph,toll,one_way,road_class".split(","))
        w.writerows(rows)
    print("roads.csv written")

if __name__=="__main__":
    write_grid()
