from flask import Flask, request, jsonify
import osmnx as ox
import pandas as pd
import os
from mega import Mega

app = Flask(__name__)

# --- CONFIG ---
RADIUS = 2000  
OUTPUT_FOLDER = "./ch_input"
MEGA_EMAIL = "sahasrabudhesoham@gmail.com"
MEGA_PASS = "Somshiv@m2"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- Login to Mega ---
mega = Mega()
m = mega.login(MEGA_EMAIL, MEGA_PASS)

# --- HELPER: Extract subgraph ---
def extract_subgraph(user_lat, user_lon, hospital_lat, hospital_lon, radius=RADIUS):
    center_lat = (user_lat + hospital_lat) / 2
    center_lon = (user_lon + hospital_lon) / 2
    subgraph = ox.graph_from_point((center_lat, center_lon), dist=radius, network_type="drive")
    return subgraph

# --- HELPER: Save edge list CSV ---
def save_edge_list(G_sub, filename):
    edges = []
    mapping = {n: i for i, n in enumerate(G_sub.nodes())}
    for u, v, data in G_sub.edges(data=True):
        w = data.get("length", 1.0)
        edges.append([mapping[u], mapping[v], w])
    df = pd.DataFrame(edges, columns=["u", "v", "weight"])
    df.to_csv(filename, index=False)

# --- API ROUTE: User selects hospital ---
@app.route("/select_hospital", methods=["POST"])
def api_select_hospital():
    data = request.json
    user_lat = data.get("user_lat")
    user_lon = data.get("user_lon")
    hospital_lat = data.get("hospital_lat")
    hospital_lon = data.get("hospital_lon")

    if None in [user_lat, user_lon, hospital_lat, hospital_lon]:
        return jsonify({"error": "Missing coordinates"}), 400

    # Extract subgraph
    G_sub = extract_subgraph(user_lat, user_lon, hospital_lat, hospital_lon)

    # Save edge list
    filename = os.path.join(OUTPUT_FOLDER, "subgraph_edges.csv")
    save_edge_list(G_sub, filename)

    # Upload to Mega
    file = m.upload(filename)
    link = m.get_upload_link(file)

    # Store metadata JSON
    metadata = {
        "user_lat": user_lat,
        "user_lon": user_lon,
        "hospital_lat": hospital_lat,
        "hospital_lon": hospital_lon,
        "csv_file": "subgraph_edges.csv",
        "mega_link": link,
    }
    json_file = os.path.join(OUTPUT_FOLDER, "subgraph_meta.json")
    pd.Series(metadata).to_json(json_file)

    # Upload JSON to Mega
    json_uploaded = m.upload(json_file)
    json_link = m.get_upload_link(json_uploaded)

    return jsonify({
        "message": "Subgraph uploaded to Mega",
        "csv_link": link,
        "json_link": json_link
    })

if __name__ == "__main__":
    app.run(debug=True)
