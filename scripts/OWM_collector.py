# owm_collector.py
# OpenWeatherMap data collector
# Collects: current weather + air quality for Prague
import requests
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()
from OWM_database import insert_weather, insert_air_quality, create_tables
# ----- tbc ---------
# Prague coordinates — OWM needs lat/lon to know WHERE
PRAGUE_LAT = 50.0755
PRAGUE_LON = 14.4378
API_KEY = os.getenv("OWM_API_KEY")

# temporary test line
# print(f"API key loaded: {API_KEY is not None}")

def get_current_weather(api_key, lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data


def parse_weather_response(raw):
    main = raw.get("main", {})
    wind = raw.get("wind", {})
    weather = raw.get("weather", [{}])
    coord = raw.get("coord", {})

    return {
        "temperature": main.get("temp"),
        "feels_like": main.get("feels_like"),
        "humidity": main.get("humidity"),
        "pressure": main.get("pressure"),
        "wind_speed": wind.get("speed"),
        "precipitation": raw.get("rain", {}).get("1h", 0.0),
        "condition": weather[0].get("description"),
        "city": raw.get("name"),
        "lat": coord.get("lat"),
        "lon": coord.get("lon"),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    }


# ----- Get air quality ----------
def get_air_quality(api_key, lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(url)
    data = response.json()
    return data


def parse_air_quality_response(raw):
    components = raw.get("list", [{}])[0].get("components", {})
    main = raw.get("list", [{}])[0].get("main", {})
    coord = raw.get("coord", {})

    return {
        "aqi": main.get("aqi"),
        "pm2_5": components.get("pm2_5"),
        "pm10": components.get("pm10"),
        "no2": components.get("no2"),
        "o3": components.get("o3"),
        "co": components.get("co"),
        "so2": components.get("so2"),
        "lat": coord.get("lat"),
        "lon": coord.get("lon"),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    }




if __name__ == "__main__":
    # make sure tables exist
    create_tables()

    # collect weather
    raw_weather = get_current_weather(API_KEY, PRAGUE_LAT, PRAGUE_LON)
    clean_weather = parse_weather_response(raw_weather)
    insert_weather(clean_weather)
    print("Weather saved:", clean_weather)

    # collect air quality
    raw_air = get_air_quality(API_KEY, PRAGUE_LAT, PRAGUE_LON)
    clean_air = parse_air_quality_response(raw_air)
    insert_air_quality(clean_air)
    print("Air quality saved:", clean_air)