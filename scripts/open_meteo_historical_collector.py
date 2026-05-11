# open_meteo_historical.py
# Fetches 80 years of historical hourly data from Open-Meteo

import requests
import time
from datetime import datetime, date
from OWM_database import insert_open_meteo, create_tables

PRAGUE_LAT = 50.0755
PRAGUE_LON = 14.4378

VARIABLES = "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,cloud_cover,shortwave_radiation,weather_code"

def fetch_chunk(start_date, end_date):
    """Fetch one chunk of historical data between two dates."""
    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={PRAGUE_LAT}&longitude={PRAGUE_LON}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&hourly={VARIABLES}&timezone=UTC"
    )
    response = requests.get(url)
    return response.json()


def parse_chunk(raw):
    hourly = raw["hourly"]
    rows = []

    for i in range(len(hourly["time"])):
        row = {
            "timestamp": hourly["time"][i],
            "lat": raw["latitude"],        # ← add this
            "lon": raw["longitude"],       # ← add this
            "temperature": hourly["temperature_2m"][i],
            "humidity": hourly["relative_humidity_2m"][i],
            "wind_speed": hourly["wind_speed_10m"][i],
            "precipitation": hourly["precipitation"][i],
            "cloud_cover": hourly["cloud_cover"][i],
            "shortwave_radiation": hourly["shortwave_radiation"][i],
            "weather_code": hourly["weather_code"][i],
        }
        rows.append(row)

    return rows



def fetch_all_historical():
    """Fetch all historical data year by year."""

    start_year = 1940
    end_year = date.today().year

    all_rows = []

    for year in range(start_year, end_year + 1):
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"

        print(f"Fetching {year}...")

        raw = fetch_chunk(start_date, end_date)
        rows = parse_chunk(raw)
        all_rows.extend(rows)

        print(f"  Got {len(rows)} rows")

        time.sleep(1)  # wait 1 second between requests

    return all_rows


if __name__ == "__main__":
    create_tables()
    total_rows = 0
    years_to_test = list(range(2022, 2025))

    for i, year in enumerate(years_to_test):
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"

        print(f"[{i + 1}/{len(years_to_test)}] Fetching {year}...", end=" ")

        raw = fetch_chunk(start_date, end_date)
        rows = parse_chunk(raw)

        # save each row to database
        for row in rows:
            insert_open_meteo(row)

        total_rows += len(rows)
        print(f" {len(rows)} rows saved (total: {total_rows})")
        time.sleep(1)

    print(f"\nDone! {total_rows} rows saved to database!")