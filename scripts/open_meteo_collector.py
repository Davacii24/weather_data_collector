# open_meteo_collector.py
# Open-Meteo data collector
# Collects: current weather for Prague (no API key needed!)
# url: https://api.open-meteo.com/v1/forecast?latitude=50.0755&longitude=14.4378&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,weather_code&timezone=UTC

import requests
from datetime import datetime, timezone
from OWM_database import create_tables, get_connection

# Prague coordinates
PRAGUE_LAT = 50.0755
PRAGUE_LON = 14.4378

def get_current_weather():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={PRAGUE_LAT}&longitude={PRAGUE_LON}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,weather_code&timezone=UTC"
    response = requests.get(url)
    return response.json()

def parse_response(raw):
    current = raw.get("current", {})
    return {
        "temperature": current.get("temperature_2m"),
        "humidity": current.get("relative_humidity_2m"),
        "wind_speed": current.get("wind_speed_10m"),
    }

if __name__ == "__main__":
    raw = get_current_weather()
    print(raw)