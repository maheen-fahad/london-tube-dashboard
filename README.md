# london-tube-dashboard
Interactive Power BI dashboard showcasing every London Underground tube station. Hover over any station to see which lines serve it, and estimated entries and exits for that station. Built with Python, Excel, and Power BI using public Transport for London (TfL) data. 

<img width="1775" height="812" alt="dashboard" src="https://github.com/user-attachments/assets/3c8de819-6a75-4ff1-8d9f-6a611242029b" />
<img width="1777" height="860" alt="tooltip" src="https://github.com/user-attachments/assets/f0913abd-b259-4da5-aa4c-e9f6c861ca8e" />

 
## tools used 
### Python (pandas, requests, rapidfuzz, openpyxl)
used to pull data from TfL API, cleaning, matching names across datasets, building final tables

### Excel
used to inspect the source data 

### Power BI 
used to create the dashboard

### Deneb (Vega-Lite custom visual)
used to illustrate coloured line segments between stations

## how each file works
**fetch stations and lines** (`fetch_stations.py`): Get TfL API for each of the 11 Underground lines and build a table with coordinates, plus a station-to-line table. 

**clean passenger data** (`clean_entry_exit.py`): Load TfL Excel file, keeping only London Underground rows, and remove stations with no figures (e.g. Kensington Olympia).

**match and merge** (`build_dataset.py`): Joins the two sources by normalised station name, with manual overrides where names differ. See the challenges section below for more info.

**build line connections** (`build_connections.py`): Uses the API's ordered station sequences to create one row per tube line between neighbouring stations on each line (378 total links).

**build the map table** (`build_map_table.py`): Combine stations and connections into one table, with line colors and accurate map coordinates

**dashboard**: Load table into Power BI and draw using a Deneb visual; station markers with coloured line segments underneath, tooltips upon hovering.

## challenges 
**Fuzzy matching (using rapidfuzz) got four cases wrong, so I had to override them manually:**
- Bank and Monument: presented as 1 station in TfL's passenger data, but 2 in the API. I merged them into one.
- Paddington: the Hammersmith and City platforms have a separate ID in the API, so I merged them into the main Paddington station.
- Edgware Road: Two separate stations that fuzzy matching confused.
- Shepherd's and Heathrow Terminals 2 and 3: Matched to the wrong neighbouring stations

**TfL's file gives a single combined annual figure per station, but entries and exits separately only for a typical day of the week.** To split the annual figure, I did the following:
- weighted the typical-day figures into a weekly 'entry vs exit' share for each station
- applied that share to the annual total
> The annual entries/exits shown on the dashboard are **estimates**, and are labelled as such.

**Power BI does not allow for the illustration of line segments between points,** so I used the Deneb custom visual (Vega-Lite) with a table of line segments.

## data sources used 
- **Station locations, line membership and line routes:** [TfL Unified API](https://api.tfl.gov.uk) (`/Line/Mode/tube`, `/Line/{id}/StopPoints`, `/Line/{id}/Route/Sequence/{direction}`)
- **Station entries and exits:** TfL's annualised station entries and exits file (2025 edition, `AC2025_AnnualisedEntryExit_public.xlsx`), published on TfL's crowding data page

Contains TfL data. Powered by TfL Open Data. This project is not affiliated with or endorsed by Transport for London.

## Author 
*Maheen Fahad B.*
> LinkedIn: Maheen Fahad
