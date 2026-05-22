import logging
logger = logging.getLogger(__name__)
import requests



# prague coordinate for function collecting
PRAGUE_LAT = 50.0755
PRAGUE_LON = 14.4378


def fetch_hourly_chunk(start_date, end_date):
    """Fetch hourly historical data between two dates."""
    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={PRAGUE_LAT}&longitude={PRAGUE_LON}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,"
        f"precipitation,cloud_cover,shortwave_radiation,"
        f"weather_code,soil_temperature_0_to_7cm"
        f"&timezone=UTC"
    )
    try:
        response = requests.get(url)
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
        f"&daily=sunrise,sunset,wind_gusts_10m_max,cloud_cover_mean,"
        f"temperature_2m_mean,temperature_2m_max,temperature_2m_min,"
        f"wind_speed_10m_max,daylight_duration,sunshine_duration,"
        f"precipitation_sum,rain_sum,snowfall_sum,precipitation_hours,"
        f"wind_direction_10m_dominant,soil_moisture_0_to_100cm_mean,"
        f"soil_moisture_0_to_7cm_mean,soil_moisture_28_to_100cm_mean,"
        f"snowfall_water_equivalent_sum"
        f"&timezone=UTC"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.info("Successfully fetched daily data: %s to %s", start_date, end_date)
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch daily data %s to %s: %s", start_date, end_date, e)
        return None