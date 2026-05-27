# function for collecting instant data
# packages
import requests
import os
import sqlite3
import pandas as pd
from datetime import datetime, timezone, date, timedelta
from dotenv import load_dotenv
from scripts.CHMU_processing import ParsedTableProcessing
from OWM_OM_parser import OWMParser, OpenMeteoParser
from OWM_database import get_connection
from scripts.CHMU_station_ids import url_creator
from scripts.CHMU_parser import CHMUAutoParser
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# prague coordinate for function collecting
PRAGUE_LAT = 50.0755
PRAGUE_LON = 14.4378
API_KEY = os.getenv("OWM_API_KEY")

TENMIN_STATION_IDS = [
    "0-20000-0-11518",
    "0-20000-0-11519",
    "0-20000-0-11520",
    "0-20000-0-11567",
    "0-203-0-10904013001",
    "0-203-0-11201020001",
    "0-203-0-11514",
    "0-203-0-11515",
]

LARGE_STATION_IDS = [
    "0-20000-0-11518",  # Ruzyně
    "0-20000-0-11519",  # Karlov
    "0-20000-0-11520",  # Libuš
    "0-20000-0-11567",  # Kbely
]

ALL_STATION_IDS = [
    "0-20000-0-11518",      # Ruzyně
    "0-20000-0-11519",      # Karlov
    "0-20000-0-11520",      # Libuš
    "0-20000-0-11567",      # Kbely
    "0-203-0-10904013001",  # Komorany
    "0-203-0-11105048001",  # Zadní Kopanina
    "0-203-0-11201020001",  # Vinohrady
    "0-203-0-11201020003",  # Chodov
    "0-203-0-11201024001",  # Břevnov
    "0-203-0-11202007001",  # Suchdol
    "0-203-0-11514",        # Klementinum
    "0-203-0-11515",        # Klementinum II
]

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
        response = requests.get(url,timeout=30)
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
        response = requests.get(url,timeout=30)
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
        response = requests.get(url,timeout=30)
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
        response = requests.get(url,timeout=30)
        response.raise_for_status()
        logger.info("Successfully fetched Open-Meteo daily data for %s", yesterday)
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch Open-Meteo daily data: %s", e)
        return None

# formed into dataframe
if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    )
    conn = get_connection()

    now = datetime.now(timezone.utc)
    today = datetime.today().strftime("%Y-%m-%d")
    conn.execute(f"DELETE FROM minute WHERE date >= '{today}'")

    #CHMU 10 minute data
    minute_list = []
    for wsi in TENMIN_STATION_IDS:
        url = url_creator("now", datetime.today().strftime("%Y%m%d"), "10m", wsi)
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            raw = response.json()
            parser = CHMUAutoParser.from_raw(raw)
            df = parser.parse()
            minute_list.append(df)
            logger.info("CHMU 10min fetched for %s", wsi)
        except requests.exceptions.RequestException as e:
            logger.error("Failed to fetch CHMU 10min for %s: %s", wsi, e)

    if minute_list:
        minute_process = ParsedTableProcessing("", minute_list)
        minute_process.concat_tables()
        minute_process._concat_df.to_sql("minute", conn, if_exists="append", index=False)
        logger.info("CHMU 10min saved")

    if now.minute < 15:
        conn.execute(f"DELETE FROM hourly WHERE date >= '{today}'")
        #CHMU hourly

        hourly_list = []
        for wsi in LARGE_STATION_IDS:
            url = url_creator("now", datetime.today().strftime("%Y%m%d"), "1h", wsi)
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                raw = response.json()
                parser = CHMUAutoParser.from_raw(raw)
                df = parser.parse()
                hourly_list.append(df)
                logger.info("CHMU 1h fetched for %s", wsi)
            except requests.exceptions.RequestException as e:
                logger.error("Failed to fetch CHMU 1h for %s: %s", wsi, e)

        if hourly_list:
            hourly_process = ParsedTableProcessing("", hourly_list)
            hourly_process.concat_tables()
            hourly_process._concat_df.to_sql("hourly", conn, if_exists="append", index=False)
            logger.info("CHMU 1h saved")

        # OWM weather
        raw = get_current_weather_OWM(API_KEY, PRAGUE_LAT, PRAGUE_LON)
        if raw is not None:
            clean = OWMParser(raw).parse_weather()        # returns dictionary
            pd.DataFrame([clean]).to_sql("owm_weather", conn, if_exists="append", index=False)
            logger.info("OWM weather data saved")

        # OWM air quality
        raw = get_air_quality_OWM(API_KEY, PRAGUE_LAT, PRAGUE_LON)
        if raw is not None:
            clean = OWMParser(raw).parse_air_quality()    # returns dictionary
            pd.DataFrame([clean]).to_sql("owm_pollution", conn, if_exists="append", index=False)
            logger.info("Air quality saved")

        # Open-Meteo hourly
        raw = get_current_hourly_weather_OM()
        if raw is not None:
            clean = OpenMeteoParser(raw).parse_hourly()   # returns dictionary
            pd.DataFrame([clean]).to_sql("open_meteo_hourly", conn, if_exists="append", index=False)
            logger.info("Hourly data saved")

    if now.hour == 8 and now.minute < 10:

        current_month = datetime.today().strftime("%Y-%m")
        conn.execute(f"DELETE FROM daily WHERE date >= '{current_month}-01'")
        conn.execute(f"DELETE FROM synoptic WHERE date >= '{current_month}-01'")

        daily_list = []
        synoptic_list = []

        for wsi in ALL_STATION_IDS:
            url = url_creator("recent", datetime.today().strftime("%Y%m"), "daily", wsi)
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                raw = response.json()
                parser = CHMUAutoParser.from_raw(raw)
                daily, synoptic = parser.parse()
                daily_list.append(daily)
                synoptic_list.append(synoptic)
                logger.info("CHMU daily fetched for %s", wsi)
            except requests.exceptions.RequestException as e:
                logger.error("Failed to fetch CHMU daily for %s: %s", wsi, e)

        if daily_list:
            daily_process = ParsedTableProcessing("", daily_list)
            daily_process.concat_tables()
            daily_process._concat_df.to_sql("daily", conn, if_exists="append", index=False)

            synoptic_process = ParsedTableProcessing("", synoptic_list)
            synoptic_process.concat_tables()
            synoptic_process._concat_df.to_sql("synoptic", conn, if_exists="append", index=False)
            logger.info("CHMU daily + synoptic saved")

        # Open-Meteo daily
        raw = get_current_daily_weather_OM()
        if raw is not None:
            OpenMeteoParser(raw).parse_daily_historical().to_sql("open_meteo_daily", conn, if_exists="append", index=False)
            logger.info("Daily data saved")
        else:
            logger.warning("Skipping daily, current hour : %s", datetime.now(timezone.utc).hour)

    conn.close()