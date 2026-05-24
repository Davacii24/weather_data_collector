import logging
logger = logging.getLogger(__name__)

import pandas as pd
import time
import requests
from owm_om_parser import OpenMeteoParser
from OWM_database import get_connection
from datetime import date, timedelta



# prague coordinate for function collecting
PRAGUE_LAT = 50.0755
PRAGUE_LON = 14.4378


def fetch_hourly_chunk(start_date, end_date):
    """Fetch hourly historical data between two dates."""
    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={PRAGUE_LAT}&longitude={PRAGUE_LON}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&hourly=temperature_2m,relative_humidity_2m,"
        f"wind_speed_10m,precipitation,weather_code,"
        f"cloud_cover,shortwave_radiation,soil_temperature_0_to_7cm,soil_temperature_7_to_28cm,soil_temperature_28_to_100cm"
        f"&timezone=UTC"
    )
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        logger.info("Successfully fetched hourly data: %s to %s", start_date, end_date)
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch hourly data %s to %s: %s", start_date, end_date, e)
        return None


def fetch_daily_chunk(start_date, end_date):
    """Fetch daily historical data between two dates."""
    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={PRAGUE_LAT}&longitude={PRAGUE_LON}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&daily=sunrise,sunset,wind_gusts_10m_max,cloud_cover_mean,temperature_2m_mean,"
        f"temperature_2m_max,temperature_2m_min,wind_speed_10m_max,daylight_duration,"
        f"sunshine_duration,precipitation_sum,rain_sum,snowfall_sum,precipitation_hours,"
        f"wind_direction_10m_dominant,soil_moisture_0_to_100cm_mean,soil_moisture_0_to_7cm_mean,"
        f"soil_moisture_28_to_100cm_mean,snowfall_water_equivalent_sum"
        f"&timezone=UTC"
    )
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        logger.info("Successfully fetched daily data: %s to %s", start_date, end_date)
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch daily data %s to %s: %s", start_date, end_date, e)
        return None


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    )

    conn = get_connection()
    total_hourly = 0
    total_daily = 0
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    # fetch 80 years historical data
    years = list(range(1996, 2007)) + list(range(2011, date.today().year))

    for i, year in enumerate(years):
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        print(f"[{i + 1}/{len(years)}] Fetching {year}...", end=" ")

        raw = fetch_hourly_chunk(start_date, end_date)
        if raw is None:
            print(f"Skipping {year}")
            continue
        rows = OpenMeteoParser(raw).parse_hourly_historical()
        pd.DataFrame(rows).to_sql("open_meteo_hourly", conn, if_exists="append", index=False)
        total_hourly += len(rows)

        raw = fetch_daily_chunk(start_date, end_date)
        if raw is None:
            print(f"Skipping {year}")
            continue
        rows = OpenMeteoParser(raw).parse_daily_historical()
        pd.DataFrame(rows).to_sql("open_meteo_daily", conn, if_exists="append", index=False)
        total_daily += len(rows)

        print(f"hourly: {total_hourly}, daily: {total_daily}")
        time.sleep(5)


    print(f"\nHourly: {total_hourly}, Daily: {total_daily}")

    # handle current year
    print(f"Fetching 2026...", end=" ")
    raw = fetch_hourly_chunk("2026-01-01", yesterday)
    if raw is not None:
        rows = OpenMeteoParser(raw).parse_hourly_historical()
        pd.DataFrame(rows).to_sql("open_meteo_hourly", conn, if_exists="append", index=False)
        total_hourly += len(rows)

    raw = fetch_daily_chunk("2026-01-01", yesterday)
    if raw is not None:
        rows = OpenMeteoParser(raw).parse_daily_historical()
        pd.DataFrame(rows).to_sql("open_meteo_daily", conn, if_exists="append", index=False)
        total_daily += len(rows)

    print(f"hourly: {total_hourly}, daily: {total_daily}")

    conn.close()