# function for collecting instant data
# packages
import requests
import os
from datetime import datetime, timezone, date, timedelta
from dotenv import load_dotenv
load_dotenv()
from OWM_database import insert_weather, insert_air_quality, create_tables


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
    response = requests.get(url)
    data = response.json()
    return data


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
    response = requests.get(url)
    data = response.json()
    return data


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
    response = requests.get(url)
    return response.json()

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
    response = requests.get(url)
    return response.json()