# function for collecting instant data
# packages
import requests
import os
import sqlite3
import pandas as pd
from datetime import datetime, timezone, date, timedelta
from dotenv import load_dotenv
load_dotenv()
import logging
logger = logging.getLogger(__name__)
from owm_om_parser import OWMParser, OpenMeteoParser
from OWM_database import get_connection

# prague coordinate for function collecting
PRAGUE_LAT = 50.0755
PRAGUE_LON = 14.4378
API_KEY = os.getenv("OWM_API_KEY")

# collecting weather data from OWM
def get_current_weather_OWM(api_key, lat, lon):
    """
        Fetches current weather data from OpenWeatherMap API.

        Args:
            api_key: OWM API key
            lat: Latitude of location
            lon: Longitude of location
        Returns:
            Raw JSON response as dictionary
        """
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.info("Successfully fetched OWM weather data")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch OWM weather: %s", e)
        return None


# collecting air quality from OWM
def get_air_quality_OWM(api_key, lat, lon):
    """
        Fetches current air quality data from OpenWeatherMap API.

        Args:
            api_key: OWM API key
            lat: Latitude of location
            lon: Longitude of location
        Returns:
            Raw JSON response as dictionary
        """
    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.info("Successfully fetched OWM weather data")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch OWM weather: %s", e)
        return None


# collect current weather data from open-meteo
def get_current_hourly_weather_OM():
    """
    fetch hourly instant data from open-meteo

    Url for variables
    return: Raw JSON response as dictionary
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={PRAGUE_LAT}&longitude={PRAGUE_LON}"
        f"&current=temperature_2m,relative_humidity_2m,"
        f"wind_speed_10m,precipitation,weather_code,"
        f"cloud_cover,shortwave_radiation,soil_temperature_0_to_7cm,soil_temperature_7_to_28cm,soil_temperature_28_to_100cm"
        f"&timezone=UTC"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.info("Successfully fetched Open-Meteo hourly data")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch Open-Meteo hourly data: %s", e)
        return None

# collect current Daily data from open-meteo
def get_current_daily_weather_OM():
    """
        fetch yesterday's daily weather data from open-meteo

        start and end dates for daily data
        Url for variables
        return: Raw JSON response as dictionary
    """
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={PRAGUE_LAT}&longitude={PRAGUE_LON}"
        f"&start_date={yesterday}&end_date={yesterday}"
        f"&daily=sunrise,sunset,wind_gusts_10m_max,cloud_cover_mean,temperature_2m_mean,"
        f"temperature_2m_max,temperature_2m_min,wind_speed_10m_max,daylight_duration,"
        f"sunshine_duration,precipitation_sum,rain_sum,snowfall_sum,precipitation_hours,"
        f"wind_direction_10m_dominant,soil_moisture_0_to_100cm_mean,soil_moisture_0_to_7cm_mean,"
        f"soil_moisture_28_to_100cm_mean,snowfall_water_equivalent_sum"
        f"&timezone=UTC"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.info("Successfully fetched Open-Meteo daily data for %s", yesterday)
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch Open-Meteo daily data: %s", e)
        return None



# formed into dataframe
if __name__ == "__main__":
    conn = get_connection()


    # OWM weather
    raw = get_current_weather_OWM(API_KEY, PRAGUE_LAT, PRAGUE_LON)
    clean = OWMParser(raw).parse_weather()        # returns dictionary
    pd.DataFrame([clean]).to_sql("owm_weather", conn, if_exists="append", index=False)
    print("Weather saved")

    # OWM air quality
    raw = get_air_quality_OWM(API_KEY, PRAGUE_LAT, PRAGUE_LON)
    clean = OWMParser(raw).parse_air_quality()    # returns dictionary
    pd.DataFrame([clean]).to_sql("owm_pollution", conn, if_exists="append", index=False)
    print("Air quality saved")

    # Open-Meteo hourly
    raw = get_current_hourly_weather_OM()
    clean = OpenMeteoParser(raw).parse_hourly()   # returns dictionary
    pd.DataFrame([clean]).to_sql("open_meteo_hourly", conn, if_exists="append", index=False)
    print("Hourly saved")

    # Open-Meteo daily
    if datetime.now(timezone.utc).hour == 0:
        raw = get_current_daily_weather_OM()
        pd.DataFrame([OpenMeteoParser(raw).parse_daily()]).to_sql("open_meteo_daily", conn, if_exists="append",
                                                                  index=False)
        print("Daily saved")
    else:
        print("skipping")

    conn.close()