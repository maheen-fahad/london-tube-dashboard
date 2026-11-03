import math
import pandas as pd
from pathlib import Path

data_dir = Path(__file__).resolve().parent.parent / "data"
stations = pd.read_csv(data_dir / "stations_final.csv")
conn = pd.read_csv(data_dir / "connections.csv")

colours = {
    "bakerloo": "#B36305", "central": "#E32017", "circle": "#FFD300",
    "district": "#00782A", "hammersmith-city": "#F3A9BB", "jubilee": "#A0A5A9",
    "metropolitan": "#9B0056", "northern": "#000000", "piccadilly": "#003688",
    "victoria": "#0098D4", "waterloo-city": "#95CDBA",
}

stations["x"] = stations["lon"] * math.cos(math.radians(51.5))
stations["y"] = stations["lat"]

pos = stations.set_index("station_id")[["x", "y"]]
seg = (conn.merge(pos, left_on="station_a", right_index=True)
           .rename(columns={"x": "x1", "y": "y1"})
           .merge(pos, left_on="station_b", right_index=True)
           .rename(columns={"x": "x2", "y": "y2"}))
seg["colour"] = seg["line_id"].map(colours)
seg["kind"] = "segment"
seg["label"] = seg["line_name"]

print("Lines with no colour:", seg[seg["colour"].isna()]["line_id"].unique().tolist())

st = stations.copy()
st["kind"] = "station"
st["label"] = st["display_name"]
st["x1"], st["y1"], st["x2"], st["y2"] = st["x"], st["y"], st["x"], st["y"]
st["colour"] = "#FFFFFF"
for c in ["annual_entries_est", "annual_exits_est"]:
    st[c] = st[c].round().astype("Int64")

cols = ["kind", "label", "colour", "x1", "y1", "x2", "y2",
        "lines_count", "lines", "annual_entries_est", "annual_exits_est"]
out = pd.concat([seg[cols[:7]], st[cols]], ignore_index=True)
out.to_csv(data_dir / "map_data.csv", index=False)

print("Segments:", len(seg), "| Stations:", len(st))