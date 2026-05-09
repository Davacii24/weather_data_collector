from pathlib import Path
from scripts.CHMU_downloader import download_weather_data
import logging
import pandas as pd
from pathlib import Path
import sqlite3
from scripts.CHMU_processing import ParsedTableProcessing
from scripts.CHMU_station_ids import station_ids, url_creator
from scripts.CHMU_parser import CHMUAutoParser
import seaborn as sns
import matplotlib.pyplot as plt


conn = sqlite3.connect("data/post_process_data/weather.db")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)

"""


output_dir = Path("data/raw_data")
#download_weather_data(output_dir, "https://opendata.chmi.cz/meteorology/climate/Klimatologicka_data_popis.pdf")

df = pd.read_csv("data/raw_data/meta1.csv")

_,ids = station_ids(df)


url = url_creator("now","20260503","yearly","0-20000-0-11519")

for i in range(len(ids)):
    url = url_creator("now","20260506","10m",ids[i])
    download_weather_data(output_dir,url)
"""
####

df = pd.read_csv("data/raw_data/meta1.csv")
_,ids = station_ids(df)

raw_folder = Path("data/raw_data")
output_dir = Path("data/raw_data")



daily_list = []
synoptic_list = []

for filepath in raw_folder.glob("dly-*.json"):
    parser = CHMUAutoParser(str(filepath), "data/post_process_data/")
    daily, synoptic = parser.load().parse()
    daily_list.append(daily)
    synoptic_list.append(synoptic)

daily_processor = ParsedTableProcessing("data/post_process_data/", daily_list)
daily_processor.concat_daily_tables()
print(f"Daily Shape: {daily_processor._concat_df.shape}")
print(daily_processor._concat_df[["date", "station", "data_richness", "temp_avg"]].head(20))
print(f"\nDaily columns to rename:\n{daily_processor._concat_df.columns.tolist()}")

synoptic_processor = ParsedTableProcessing("data/post_process_data/", synoptic_list)
synoptic_processor.concat_daily_tables()
print(f"\nSynoptic Shape: {synoptic_processor._concat_df.shape}")
print(f"\nSynoptic columns to rename:\n{synoptic_processor._concat_df.columns.tolist()}")

synoptic_processor._concat_df.to_sql("synoptic", conn, if_exists="replace", index=False)

daily_processor._concat_df.to_sql("daily", conn, if_exists="replace", index=False)

print(pd.read_sql("SELECT * FROM daily LIMIT 5", conn))
print(pd.read_sql("SELECT * FROM synoptic LIMIT 5", conn))

print(pd.read_sql("SELECT station, temp_avg FROM daily WHERE date LIKE '2026-05-03%' AND data_richness = 'LARGE'", conn))
df = pd.read_sql("SELECT date, station, temperature FROM synoptic WHERE temperature IS NOT NULL", conn)
#print(df.head(20))
#print(df.shape)


results = (
    df
    .assign(date = lambda x: pd.to_datetime(x['date'],errors='coerce',format= "mixed",dayfirst=True),)
    .assign(hour = lambda x: x['date'].dt.hour)
    .assign(time_of_day = lambda x: x["hour"].map({6:"Morning",13:"Afternoon",20: "Evening"}))
)
