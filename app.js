const map = L.map("map").setView(
    [12.904, 77.504],
    14
);

L.tileLayer(
    "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        maxZoom: 19
    }
).addTo(map);

let routeLayer = null;

async function findRoute(){

    try{

        const src =
            document.getElementById("src").value;

        const dst =
            document.getElementById("dst").value;

        const objective =
            document.getElementById("objective").value;

        const trafficU =
            document.getElementById("traffic_u").value;

        const trafficV =
            document.getElementById("traffic_v").value;

        const closeU =
            document.getElementById("close_u").value;

        const closeV =
            document.getElementById("close_v").value;

        let traffic_edges = [];
        let close_edges = [];

        if(
            trafficU.trim() !== "" &&
            trafficV.trim() !== ""
        ){
            traffic_edges.push([
                trafficU,
                trafficV
            ]);
        }

        if(
            closeU.trim() !== "" &&
            closeV.trim() !== ""
        ){
            close_edges.push([
                closeU,
                closeV
            ]);
        }

        const response =
            await fetch(
                "http://127.0.0.1:8000/route",
                {
                    method:"POST",

                    headers:{
                        "Content-Type":
                        "application/json"
                    },

                    body:JSON.stringify({

                        src,
                        dst,
                        objective,

                        alpha:1,
                        beta:0.2,
                        gamma:5,

                        traffic_edges,
                        close_edges
                    })
                }
            );

        const data =
            await response.json();

        document
        .getElementById("result")
        .innerHTML =

        `
        <h3>Route Found</h3>

        <p>
        <b>ETA:</b>
        ${data.eta_sec} sec
        </p>

        <p>
        <b>Path:</b>
        </p>

        <p>
        ${data.path.join(" → ")}
        </p>

        <p>
        <b>Traffic:</b>
        ${
            traffic_edges.length
            ?
            traffic_edges[0].join(" → ")
            :
            "None"
        }
        </p>

        <p>
        <b>Closed Road:</b>
        ${
            close_edges.length
            ?
            close_edges[0].join(" → ")
            :
            "None"
        }
        </p>
        `;

        if(routeLayer){

            map.removeLayer(
                routeLayer
            );
        }

        routeLayer =
            L.geoJSON(
                data.geojson,
                {
                    style:{
                        color:"red",
                        weight:6
                    }
                }
            ).addTo(map);

        map.fitBounds(
            routeLayer.getBounds()
        );

    }
    catch(error){

        console.error(error);

        alert(
            "Error: " +
            error.message
        );
    }
}

async function loadAlternatives(){

    try{

        const src =
            document.getElementById("src").value;

        const dst =
            document.getElementById("dst").value;

        const response =
            await fetch(
                `http://127.0.0.1:8000/alternatives?src=${src}&dst=${dst}&k=5`
            );

        const data =
            await response.json();

        let html =
            "<h3>Alternative Routes</h3>";

        data.forEach((route,index)=>{

            html +=
            `
            <div class="alt-card">

                <b>
                Route ${index+1}
                </b>

                <br><br>

                Time:
                ${route.time_sec}
                sec

                <br>

                Distance:
                ${route.dist_m}
                m

                <br>

                Tolls:
                ${route.tolls}

            </div>
            `;
        });

        document
        .getElementById(
            "alternatives"
        )
        .innerHTML = html;

    }
    catch(error){

        console.error(error);

        alert(
            "Failed to load alternatives."
        );
    }
}