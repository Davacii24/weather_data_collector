# open_meteo_collector.py
# Open-Meteo data collector
# Collects: current weather for Prague (no API key needed!)
# url: https://api.open-meteo.com/v1/forecast?latitude=50.0755&longitude=14.4378&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,weather_code&timezone=UTC

import requests
from datetime import datetime, timezone
from OWM_database import create_tables, insert_open_meteo

# Prague coordinates
PRAGUE_LAT = 50.0755
PRAGUE_LON = 14.4378


def get_current_weather():
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={PRAGUE_LAT}&longitude={PRAGUE_LON}"
        f"&current=temperature_2m,relative_humidity_2m,"
        f"wind_speed_10m,precipitation,weather_code,"
        f"cloud_cover,shortwave_radiation,soil_temperature_0_to_7cm"
        f"&timezone=UTC"
    )
    response = requests.get(url)
    return response.json()

def parse_response(raw):
    current = raw.get("current", {})
    return {
        "timestamp": current.get("time"),
        "lat": raw.get("latitude"),
        "lon": raw.get("longitude"),
        "temperature": current.get("temperature_2m"),
        "humidity": current.get("relative_humidity_2m"),
        "wind_speed": current.get("wind_speed_10m"),
        "precipitation": current.get("precipitation"),
        "cloud_cover": current.get("cloud_cover"),
        "shortwave_radiation": current.get("shortwave_radiation"),
        "weather_code": current.get("weather_code"),
        "soil_temperature": current.get("soil_temperature_0_to_7cm")
    }

if __name__ == "__main__":
    create_tables()
    raw = get_current_weather()
    clean = parse_response(raw)
    insert_open_meteo(clean)
    print(" Live weather saved:", clean)