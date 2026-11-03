import requests
import pandas as pd
from pathlib import Path

BASE = "https://api.tfl.gov.uk"
data_dir = Path(__file__).resolve().parent.parent / "data"

stations_raw = pd.read_csv(data_dir / "stations.csv")
final = pd.read_csv(data_dir / "stations_final.csv")
valid_ids = set(final["station_id"])

def find_id(text):
    hits = stations_raw[stations_raw["station_name"].str.contains(text, regex=False, case=False)]
    if len(hits) != 1:
        raise ValueError(f"'{text}' matched {len(hits)} stations")
    return hits.iloc[0]["station_id"]

merge_map = {
    find_id("Monument Underground Station"): find_id("Bank Underground Station"),
    find_id("Paddington (H&C"): find_id("Paddington Underground Station"),
}

lines = requests.get(f"{BASE}/Line/Mode/tube").json()

edges = set()
for line in lines:
    for direction in ["outbound", "inbound"]:
        r = requests.get(f"{BASE}/Line/{line['id']}/Route/Sequence/{direction}")
        r.raise_for_status()
        for seq in r.json().get("stopPointSequences", []):
            ids = [merge_map.get(s["id"], s["id"]) for s in seq["stopPoint"]]
            for a, b in zip(ids, ids[1:]):
                if a != b:
                    first, second = sorted([a, b])
                    edges.add((line["id"], line["name"], first, second))
    print(line["name"], "done")

conn = pd.DataFrame(sorted(edges), columns=["line_id", "line_name", "station_a", "station_b"])

missing = set(conn["station_a"]).union(conn["station_b"]) - valid_ids
print("\nStation IDs in connections but not in final table:", len(missing))
print(sorted(missing))
conn = conn[conn["station_a"].isin(valid_ids) & conn["station_b"].isin(valid_ids)]

conn.to_csv(data_dir / "connections.csv", index=False)
conn.to_excel(data_dir / "connections.xlsx", index=False)

print("\nConnections per line:")
print(conn.groupby("line_name").size().to_string())
print("\nTotal connections:", len(conn))