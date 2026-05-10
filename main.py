import time
from pathlib import Path
from scripts.CHMU_downloader import download_weather_data, batch_downloader
import logging
import pandas as pd
from pathlib import Path
import sqlite3
from scripts.CHMU_processing import ParsedTableProcessing
from scripts.CHMU_station_ids import station_ids, url_creator
from scripts.CHMU_parser import CHMUAutoParser
import seaborn as sns

import matplotlib.pyplot as plt
import time

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

LARGE_STATION_IDS_HOURLY = [
    "0-20000-0-11518",  # Ruzyně
    "0-20000-0-11519",  # Karlov
    "0-20000-0-11520",  # Libuš
    "0-20000-0-11567",  # Kbely
]

TENMIN_STATION_IDS = [
    "0-20000-0-11518",      # Ruzyně
    "0-20000-0-11519",      # Karlov
    "0-20000-0-11520",      # Libuš
    "0-20000-0-11567",      # Kbely
    "0-203-0-10904013001",  # Komorany
    "0-203-0-11201020001",  # Vinohrady
    "0-203-0-11514",        # Klementinum
    "0-203-0-11515",        # Klementinum II
]

df = pd.read_csv("data/raw_data/meta1.csv")
historic_ids,ids = station_ids(df)

raw_folder = Path("data/raw_data")
output_dir = Path("data/raw_data")

#batch_downloader(TENMIN_STATION_IDS, "recent", "10min", "202605")

hourly_list = []
total_rows = 0
start = time.time()

for filepath in raw_folder.glob("1h-*.json"):
    parser = CHMUAutoParser(str(filepath), "data/post_process_data/")
    hourly = parser.load().parse()
    total_rows += hourly.shape[0]
    hourly_list.append(hourly)

elapsed = time.time() - start
print(f"\nParsed {len(hourly_list)} files → {total_rows} rows in {elapsed:.2f}s")
print(f"Avg: {elapsed/len(hourly_list):.3f}s per file")

minute_list = []
total_rows = 0
start = time.time()

for filepath in raw_folder.glob("10m-*.json"):
    parser = CHMUAutoParser(str(filepath), "data/post_process_data/")
    minute = parser.load().parse()
    total_rows += minute.shape[0]
    minute_list.append(minute)

elapsed = time.time() - start
print(f"\nParsed {len(minute_list)} files → {total_rows} rows in {elapsed:.2f}s")
print(f"Avg: {elapsed/len(minute_list):.3f}s per file")

#####
hourly_process = ParsedTableProcessing("data/post_process_data/" ,hourly_list)
hourly_process.concat_tables()

minute_process = ParsedTableProcessing("data/post_process_data/" ,minute_list)
minute_process.concat_tables()

hourly_process._concat_df.to_sql("hourly", conn, if_exists="replace", index=False)
minute_process._concat_df.to_sql("minute", conn, if_exists="replace", index=False)

df = pd.read_sql("SELECT date, AVG(temperature) as avg_temp FROM minute WHERE temperature IS NOT NULL GROUP BY date ORDER BY date", conn)
df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date").resample("1h").mean().reset_index()
print(df.head())

df_hourly = df.set_index("date").resample("1h").mean().reset_index()

fig, ax = plt.subplots(figsize=(18, 6))
ax.plot(df_hourly["date"], df_hourly["avg_temp"], linewidth=0.8, alpha=0.9)
ax.fill_between(df_hourly["date"], df_hourly["avg_temp"], alpha=0.15)
ax.set_xlabel("Date", fontsize=12)
ax.set_ylabel("Temperature (°C)", fontsize=12)
ax.set_title("Average Prague Temperature (10-min stations, hourly resampled)", fontsize=14)
ax.grid(True, alpha=0.3)
fig.tight_layout()
plt.show()



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

#print(pd.read_sql("SELECT * FROM daily LIMIT 5", conn))
#print(pd.read_sql("SELECT * FROM synoptic LIMIT 5", conn))

#print(pd.read_sql("SELECT station, temp_avg FROM daily WHERE date LIKE '2026-05-03%' AND data_richness = 'LARGE'", conn))
df = pd.read_sql("SELECT date, station, temperature FROM synoptic WHERE temperature IS NOT NULL", conn)
#print(df.head(20))
#print(df.shape)


results = (
    df
    .assign(date=lambda x: pd.to_datetime(x['date']))
    .assign(hour = lambda x: x['date'].dt.hour)
    .assign(time_of_day = lambda x: x["hour"].map({6:"Morning",13:"Afternoon",20: "Evening"}))
)

sunshine_df = pd.read_sql("SELECT date, station, sunshine_hours FROM daily WHERE sunshine_hours IS NOT NULL", conn)
sunshine_df["date"] = pd.to_datetime(sunshine_df["date"])
sunshine_df["date"] = sunshine_df["date"].dt.date

sunshine_pivot = sunshine_df.pivot_table(index="station", columns="date", values="sunshine_hours")

fig, ax = plt.subplots(figsize=(16, 5))
sns.heatmap(sunshine_pivot, cmap="YlOrRd", ax=ax, cbar_kws={"label": "Sunshine Duration (hours)"})
ax.set_title("Sunshine Duration Across Prague Stations")
ax.set_xlabel("Date")
ax.set_ylabel("")
plt.tight_layout()
#plt.show()
