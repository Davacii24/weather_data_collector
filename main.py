from datetime import datetime

from scripts.CHMU_downloader import download_weather_data, batch_downloader
import logging
import pandas as pd
from pathlib import Path
import sqlite3
from scripts.CHMU_processing import ParsedTableProcessing
from scripts.CHMU_station_ids import station_ids, url_creator
from scripts.CHMU_parser import CHMUAutoParser
from scripts.OM_historical_downloader import OM_historical_downloader

import time


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)

df = pd.read_csv("data/raw_data/meta1.csv")
historic_ids,ids = station_ids(df)

LARGE_STATION_IDS = [
    "0-20000-0-11518",  # Ruzyně
    "0-20000-0-11519",  # Karlov
    "0-20000-0-11520",  # Libuš
    "0-20000-0-11567",  # Kbely
]

HISTORICAL_STATION_IDS_DAILY = [
    "0-20000-0-11518",  # Ruzyně
    "0-20000-0-11519",  # Karlov
    "0-20000-0-11520",  # Libuš
    "0-20000-0-11567",  # Kbely
    "0-203-0-11514",    # Klementinum OLD
    "0-000-0-00000",    # Intentional bad ID — error handling demo
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

raw_folder = Path("data/raw_data")
output_dir = Path("data/raw_data")

def main():
    conn = sqlite3.connect("data/weather.db")

    OM_historical_downloader(conn)
    batch_downloader(TENMIN_STATION_IDS, "recent", "10min", "202601",output_dir)
    batch_downloader(LARGE_STATION_IDS, "recent", "1hour", "202601",output_dir)
    batch_downloader(ids, "recent", "daily", "202601",output_dir)

    for wsi in HISTORICAL_STATION_IDS_DAILY:
        url = url_creator("historical","-","daily",wsi)
        download_weather_data(output_dir,url)

    for year in range(2018,2026):
        batch_downloader(LARGE_STATION_IDS, "historical", "10min", str(year),output_dir)

    for wsi in TENMIN_STATION_IDS:
        url = url_creator("now",datetime.today().strftime("%Y%m%d"),"10m",wsi)
        download_weather_data(output_dir,url)

    for wsi in LARGE_STATION_IDS:
        url = url_creator("now",datetime.today().strftime("%Y%m%d"),"1h",wsi)
        download_weather_data(output_dir,url)

    hourly_list = []
    total_rows = 0
    start = time.time()

    for filepath in raw_folder.glob("1h-*.json"):
        parser = CHMUAutoParser(str(filepath), "data/post_process_data/")
        hourly = parser.load().parse()
        total_rows += hourly.shape[0]
        hourly_list.append(hourly)

    elapsed = time.time() - start
    print(f"\nParsed {len(hourly_list)} files with {total_rows} rows in {elapsed:.2f}s")
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
    print(f"\nParsed {len(minute_list)} files with {total_rows} rows in {elapsed:.2f}s")
    print(f"Avg: {elapsed/len(minute_list):.3f}s per file")

    daily_list = []
    synoptic_list = []
    total_rows = 0
    start = time.time()

    for filepath in raw_folder.glob("dly-*.json"):
        parser = CHMUAutoParser(str(filepath), "data/post_process_data/")
        daily, synoptic = parser.load().parse()
        total_rows += daily.shape[0]
        total_rows += synoptic.shape[0]
        daily_list.append(daily)
        synoptic_list.append(synoptic)

    elapsed = time.time() - start
    print(f"\nParsed {len(daily_list)} files with  {total_rows} rows in {elapsed:.2f}s")
    print(f"Avg: {elapsed/len(daily_list):.3f}s per file")


    hourly_process = ParsedTableProcessing("data/post_process_data/" ,hourly_list)
    hourly_process.concat_tables()

    minute_process = ParsedTableProcessing("data/post_process_data/" ,minute_list)
    minute_process.concat_tables()

    daily_process = ParsedTableProcessing("data/post_process_data/" ,daily_list)
    daily_process.concat_tables()

    synoptic_process = ParsedTableProcessing("data/post_process_data/" ,synoptic_list)
    synoptic_process.concat_tables()


    hourly_process._concat_df.to_sql("hourly", conn, if_exists="replace", index=False)
    minute_process._concat_df.to_sql("minute", conn, if_exists="replace", index=False)
    daily_process._concat_df.to_sql("daily", conn, if_exists="replace", index=False)
    synoptic_process._concat_df.to_sql("synoptic", conn, if_exists="replace", index=False)

    conn.close()

if __name__ == "__main__":
    main()
