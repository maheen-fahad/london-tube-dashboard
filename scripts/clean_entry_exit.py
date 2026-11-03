import pandas as pd
from pathlib import Path

data_dir = Path(__file__).resolve().parent.parent / "data"
path = data_dir / "AC2025_AnnualisedEntryExit_public.xlsx"

cols = ["mode", "mnlc", "masc", "station_raw", "coverage", "source",
        "entry_mon", "entry_midweek", "entry_fri", "entry_sat", "entry_sun",
        "exit_mon", "exit_midweek", "exit_fri", "exit_sat", "exit_sun",
        "weekly", "twelve_week", "annualised"]

df = pd.read_excel(path, sheet_name="AC25_v08.2_E9_annualised",
                   skiprows=7, header=None, usecols="A:S", names=cols)

df = df[df["mode"] == "LU"].copy()

num_cols = cols[6:] 
df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")

bad = df[df[num_cols].isna().any(axis=1)]
print("Rows with missing/non-numeric values:", len(bad))
print(bad[["station_raw"] + num_cols[:2]].head())

df = df.dropna(subset=["annualised"])

df["station_name"] = (df["station_raw"].astype(str)
                      .str.replace(r"\s+LU$", "", regex=True)
                      .str.strip())

df["week_entries"] = (df["entry_mon"] + 3 * df["entry_midweek"]
                      + df["entry_fri"] + df["entry_sat"] + df["entry_sun"])
df["week_exits"] = (df["exit_mon"] + 3 * df["exit_midweek"]
                    + df["exit_fri"] + df["exit_sat"] + df["exit_sun"])

share = df["week_entries"] / (df["week_entries"] + df["week_exits"])
df["annual_entries_est"] = (df["annualised"] * share).round()
df["annual_exits_est"] = (df["annualised"] * (1 - share)).round()

out = df[["station_name", "annualised", "annual_entries_est", "annual_exits_est"]]
out.to_csv(data_dir / "entry_exit_clean.csv", index=False)

print("Underground rows:", len(out))
print(out.sort_values("annualised", ascending=False).head(10))