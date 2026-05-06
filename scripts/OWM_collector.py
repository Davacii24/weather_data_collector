# owm_collector.py
# OpenWeatherMap data collector
# Collects: current weather + air quality for Prague
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
# ----- tbc ---------
# Prague coordinates — OWM needs lat/lon to know WHERE
PRAGUE_LAT = 50.0755
PRAGUE_LON = 14.4378
API_KEY = os.getenv("OWM_API_KEY")

# temporary test line
# print(f"API key loaded: {API_KEY is not None}")

def get_current_weather(api_key, lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    # Step 2: send request
    # hint: exactly like your practice!
    # response = requests.get(???)

    # Step 3: return as dictionary
    # hint: what method turns response into a dictionary?
    pass

def parse_weather_response(raw):
    # raw is the messy nested dictionary from OWM
    # this cleans and flattens it — exactly like Exercise 3!
    pass