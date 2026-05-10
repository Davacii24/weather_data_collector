# GOAL FOR TODAY : 1. Make downloading from python
#                : 2. Basic Parsing
import time
from datetime import datetime

import requests
from pathlib import Path
import json
import logging

from envs.r_env.Lib.asyncio import sleep

from scripts.CHMU_station_ids import url_creator

#logging setup
logger = logging.getLogger(__name__)

# Specifies the output directory to our data folder
output_dir = Path("data/raw_data")
output_dir.mkdir(parents=True, exist_ok=True) # parents=True - creates folder, # exist_ok=True - no crash when exists

def download_weather_data(output_dir, weather_url):
    """
    Downloads a file from a URL and saves it to a specified folder.

    Supports CSVs, PDFs and JSON files.( ALL of these are in the CMHU)
    Handles Errors.

    Args:
        output_dir: Directory to save the downloaded file.
        arg weather_url: URL of the specified folder in CHMU
    Returns:
        Returns a nice message when succsefull
    """

    # raise error block, attempts download, raises error
    try:
        response = requests.get(weather_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        logger.error("Download failed for %s: %s", weather_url, err)
        return

    filename = weather_url.split("/")[-1]
    file_path = output_dir / filename

    if filename.endswith(".pdf"):
        to_be_saved = response.content  # content is used for pdfs
        with open(file_path, 'wb') as f:
            f.write(to_be_saved)

    elif filename.endswith(".csv"):
        to_be_saved = response.text     # text is used for csv
        with open(file_path, 'w', encoding= "utf-8") as f: # utf8 is important here, otherwise it will not work
            f.write(to_be_saved)

    elif filename.endswith(".json"):
        to_be_saved = response.json()   # jsons
        with open(file_path, 'w') as f:
            json.dump(to_be_saved, f)
    else:
        logger.warning("Unsupported file type: %s", filename)
        return

    logger.info("Success! %s downloaded to : %s", filename, file_path)
    return

def batch_downloader(station_ids,section,time_type, date_from):

    end_month = datetime.today().month
    start_month = date_from[4:6]
    dates = range(int(start_month),end_month )

    months = []
    for i in dates:
        x = (f"{date_from[0:4]}{i:02d}")
        months.append(x)

    for month in months:
        for wsi in station_ids:
            url = url_creator(section,month,time_type,wsi)
            download_weather_data(output_dir, url)
            time.sleep(1)

    dates = range(1, datetime.today().day)
    days = [f"{date_from[0:4]}{end_month:02d}{i:02d}" for i in dates]

    for day in days:
        for wsi in station_ids:
            url = url_creator(section, day, time_type, wsi)
            download_weather_data(output_dir, url)
            time.sleep(1)






