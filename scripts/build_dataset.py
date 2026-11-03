import re
import pandas as pd
from pathlib import Path

data_dir = Path(__file__).resolve().parent.parent / "data"
stations = pd.read_csv(data_dir / "stations.csv")
station_lines = pd.read_csv(data_dir / "station_lines.csv")
passengers = pd.read_csv(data_dir / "entry_exit_clean.csv")

def normalise(name):
    name = str(name).lower().replace("&", "and")
    name = re.sub(r"underground station|\btfl\b|\blu\b|\brail station\b", "", name)
    name = re.sub(r"[^a-z0-9 ]", " ", name)
    name = re.sub(r"\bst\b", "saint", name)
    return re.sub(r"\s+", " ", name).strip()

def find_id(text):
    """Find exactly one station whose name contains the text."""
    hits = stations[stations["station_name"].str.contains(text, regex=False, case=False)]
    if len(hits) != 1:
        raise ValueError(f"'{text}' matched {len(hits)} stations: {hits['station_name'].tolist()}")
    return hits.iloc[0]["station_id"]

bank = find_id("Bank Underground Station")
paddington = find_id("Paddington Underground Station")
merge_map = {
    find_id("Monument Underground Station"): bank,
    find_id("Paddington (H&C"): paddington,
}
station_lines["station_id"] = station_lines["station_id"].replace(merge_map)
station_lines = station_lines.drop_duplicates(["station_id", "line_id"])
stations = stations[~stations["station_id"].isin(merge_map.keys())].copy()

# 2. Recalculate lines per station and a readable list of them
lines_summary = (station_lines.groupby("station_id")
                 .agg(lines_count=("line_id", "nunique"),
                      lines=("line_name", lambda s: ", ".join(sorted(set(s)))))
                 .reset_index())
stations = stations.drop(columns=["lines_count"]).merge(lines_summary, on="station_id")

overrides = {
    "Bank and Monument": bank,
    "Edgware Road (DIS)": find_id("Edgware Road (Circle Line)"),
    "Edgware Road (Bak)": find_id("Edgware Road (Bak"),
    "Hammersmith (DIS)": find_id("Hammersmith (Dist"),
    "Hammersmith (H&C)": find_id("Hammersmith (H&C"),
    "Shepherd's Bush": find_id("Bush (Central)"),
    "Heathrow Terminals 123": find_id("Terminals 2 & 3"),
}

stations["key"] = stations["station_name"].apply(normalise)
key_to_id = dict(zip(stations["key"], stations["station_id"]))

passengers["station_id"] = passengers["station_name"].map(overrides)
by_key = passengers["station_name"].apply(normalise).map(key_to_id)
passengers["station_id"] = passengers["station_id"].fillna(by_key)

unmatched = passengers[passengers["station_id"].isna()]
print("Passenger rows with no station match:", len(unmatched))
print(unmatched["station_name"].tolist())

pax = (passengers.dropna(subset=["station_id"])
       .groupby("station_id")[["annualised", "annual_entries_est", "annual_exits_est"]]
       .sum().reset_index())
final = stations.merge(pax, on="station_id", how="left")

final["display_name"] = (final["station_name"]
    .str.replace(r"[\s-]*Underground( Station)?$", "", regex=True).str.strip())
final.loc[final["station_id"] == bank, "display_name"] = "Bank and Monument"

final = final[["station_id", "display_name", "lat", "lon", "lines_count", "lines",
               "annualised", "annual_entries_est", "annual_exits_est"]]

final.to_csv(data_dir / "stations_final.csv", index=False)
final.to_excel(data_dir / "stations_final.xlsx", index=False)
station_lines.to_csv(data_dir / "station_lines_final.csv", index=False)

print("\nStations in final table:", len(final))
print("Stations with no passenger data:", final["annualised"].isna().sum())
print(final[final["annualised"].isna()]["display_name"].tolist())
print("\nMost lines:")
print(final.sort_values("lines_count", ascending=False)
      [["display_name", "lines_count", "lines"]].head(8).to_string(index=False))