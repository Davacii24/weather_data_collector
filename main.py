from pathlib import Path
from scripts.CHMU_downloader import download_weather_data
import logging
import pandas as pd

from scripts.CHMU_station_ids import station_ids, url_creator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)

output_dir = Path("data/raw_data")
download_weather_data(output_dir, "https://opendata.chmi.cz/meteorology/climate/historical_csv/metadata/meta1.csv")

df = pd.read_csv("data/raw_data/meta1.csv")

ids = station_ids(df)

url = url_creator("now","10m","20260503","0-20000-0-11518")

download_weather_data(output_dir,url)