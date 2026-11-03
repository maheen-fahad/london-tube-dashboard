import requests
import pandas as pd
from pathlib import Path

BASE = "https://api.tfl.gov.uk"

data_dir = Path(__file__).resolve().parent.parent / "data"
data_dir.mkdir(exist_ok=True)

lines = requests.get(f"{BASE}/Line/Mode/tube").json()
tube_lines = {line["id"]: line["name"] for line in lines}
print("Tube lines:", list(tube_lines.values()))

stations = {}
station_lines = []

for line_id, line_name in tube_lines.items():
    response = requests.get(f"{BASE}/Line/{line_id}/StopPoints")
    response.raise_for_status()

    for stop in response.json():
        station_id = stop["id"]

        stations[station_id] = {
            "station_id": station_id,
            "station_name": stop["commonName"],
            "lat": stop["lat"],
            "lon": stop["lon"],
        }
        station_lines.append({
            "station_id": station_id,
            "line_id": line_id,
            "line_name": line_name,
        })

    print(f"{line_name}: done")

stations_df = pd.DataFrame(stations.values())
station_lines_df = pd.DataFrame(station_lines).drop_duplicates()

line_counts = (
    station_lines_df.groupby("station_id")["line_id"]
    .nunique()
    .rename("lines_count")
    .reset_index()
)
stations_df = stations_df.merge(line_counts, on="station_id")

stations_df.to_csv(data_dir / "stations.csv", index=False)
station_lines_df.to_csv(data_dir / "station_lines.csv", index=False)

print("\nStations found:", len(stations_df))
print(stations_df.sort_values("lines_count", ascending=False).head(10))