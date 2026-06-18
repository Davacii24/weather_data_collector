# Prague Weather Data Collector & Dashboard

A fully automated weather data pipeline for Prague, collecting real-time observations from multiple sources, storing them in SQLite, and visualizing them through an interactive Streamlit dashboard. Includes 250 years of historical temperature data from the ČHMÚ Klementinum station.

> **Live dashboard:** [https://weatherdatacollector-5t645ijfx9mmecyxvsltop.streamlit.app]

---

## Data sources

We have data for prague from 3 different sources. We collect them from 2 APIs(OWN and Open-Meteo) and we also 
collect data from 12 meteorological stations across prague.

### Automated data collection
- GitHub Actions runs on a schedule to collect fresh weather observations
- Data is deduplicated and stored in SQLite (`weather_live.db`)
- The updated database is committed back to the repository automatically
- Data is shown on the stramlit dash board.


### Dashboard (Page 1 — Current weather)
- Live temperature readings from 4 Prague stations with 30-minute delta arrows
- Sunrise, solar noon, and sunset times
- Temperature trend chart with min/max bands across all stations (past 30 days)
- Precipitation bar chart by station

### Analysis (Page 2 — Historical)
- **250-year temperature trend** with interactive rolling average (1775–2026)
- **Extreme temperature days by period** — hot vs cold days grouped by 20-year periods
- **Top 10 hottest and coldest days** on record
- 14 static analysis charts covering air quality, soil temperature, solar radiation, pollutant composition, correlation heatmaps, and cross-validation between data sources

## Authors

- [Yun Lee Tzun]
- [Tibor Nemeth]
