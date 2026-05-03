# owm_collector.py
# OpenWeatherMap data collector
# Collects: current weather + air quality for Prague
import requests
import os
from datetime import datetime
# ----- tbc ---------
# Prague coordinates — OWM needs lat/lon to know WHERE
PRAGUE_LAT = 50.0755
PRAGUE_LON = 14.4378

# API key loaded from .env file — NEVER hardcode this in your code
# because you push to GitHub and the key would be public!
API_KEY = os.getenv("OWM_API_KEY")

def get_current_weather(api_key, lat, lon):
    # Step 1: build the URL with your key + coordinates
    # Step 2: send request → get response (a big dictionary)
    # Step 3: return raw response
    pass

def parse_weather_response(raw):
    # raw is the messy nested dictionary from OWM
    # this cleans and flattens it — exactly like Exercise 3!
    pass