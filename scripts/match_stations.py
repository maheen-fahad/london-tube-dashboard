import re
import pandas as pd
from pathlib import Path
from rapidfuzz import process, fuzz

data_dir = Path(__file__).resolve().parent.parent / "data"
stations = pd.read_csv(data_dir / "stations.csv")
passengers = pd.read_csv(data_dir / "entry_exit_clean.csv")

def normalise(name):
    name = str(name).lower()
    name = name.replace("&", "and")
    name = re.sub(r"underground station|\btfl\b|\blu\b|\brail station\b", "", name)
    name = re.sub(r"[^a-z0-9 ]", " ", name)
    name = re.sub(r"\bst\b", "saint", name)
    return re.sub(r"\s+", " ", name).strip()

stations["key"] = stations["station_name"].apply(normalise)
passengers["key"] = passengers["station_name"].apply(normalise)

station_keys = stations["key"].unique().tolist()

rows = []
for _, p in passengers.iterrows():
    if p["key"] in station_keys:
        match, score, kind = p["key"], 100, "exact"
    else:
        result = process.extractOne(p["key"], station_keys, scorer=fuzz.token_sort_ratio)
        match, score, kind = result[0], round(result[1]), "fuzzy"
    rows.append({
        "passenger_name": p["station_name"],
        "matched_station_key": match,
        "score": score,
        "match_type": kind,
    })

report = pd.DataFrame(rows)
report.to_csv(data_dir / "match_report.csv", index=False)

print("Exact matches:", (report["match_type"] == "exact").sum())
print("Fuzzy matches:", (report["match_type"] == "fuzzy").sum())

print("\nFuzzy matches to check by eye:")
print(report[report["match_type"] == "fuzzy"]
      .sort_values("score").to_string(index=False))

used = set(report["matched_station_key"])
unused = stations[~stations["key"].isin(used)]
print("\nStations in stations.csv with no passenger data matched:")
print(unused[["station_name", "lines_count"]].to_string(index=False))