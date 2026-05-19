import time
from datetime import datetime
from tqdm import tqdm
import requests
import json
import logging
from scripts.CHMU_station_ids import url_creator

logger = logging.getLogger(__name__)

# Specifies the output directory to our data folder

def download_weather_data(output_dir, weather_url):
    """
    Downloads a file from a URL and saves it to a specified folder.

    Supports CSVs, PDFs and JSON files.( ALL of these are in the CMHU)
    Handles Errors.

    Args:
        output_dir: Directory to save the downloaded file.
        weather_url: URL of the specified folder in CHMU
    Returns:
        logs a nice message when sucsess
    """

    # raise error block, attempts download, raises error
    try:
        response = requests.get(weather_url,timeout = 30)

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

    logger.info("SUCCESS - %s downloaded to : %s", filename, file_path)
    return

def batch_downloader(station_ids,section,time_type, date_from,output_dir):
    """
    this function downloads the data in batches which automatically figures out the number of batches dates and number
    of files to download and downloads then.

    Args:
        station_ids: list of station IDs
        section: section of data to download
        time_type: type of data to download
        date_from: start date of data to download
        output_dir: directory to save the downloaded data
    """
    logger.info("Batch download started for : %s" ,station_ids)
    logging.getLogger().setLevel(logging.WARNING)

    if section == "historical":
        for i in tqdm(range(1,13)):
            for wsi_code in station_ids:
                url = url_creator(section,f"{date_from[0:4]}{i:02d}",time_type,wsi_code)
                download_weather_data(output_dir, url)
                time.sleep(0.5)
        return

    end_month = datetime.today().month
    start_month = date_from[4:6]
    dates = range(int(start_month), end_month)

    months = []
    for i in dates:
        x = (f"{date_from[0:4]}{i:02d}")
        months.append(x)

    if time_type == "daily":
        months.append(f"{date_from[0:4]}{end_month:02d}")

    dates = range(1, datetime.today().day)
    days = [f"{date_from[0:4]}{end_month:02d}{i:02d}" for i in dates]

    if time_type == "daily":
        pbar = tqdm(total=len(months) * len(station_ids), unit="file")
    else:
        pbar = tqdm(total=len(months) * len(station_ids) + len(days) * len(station_ids), unit="file")

    for month in months:
        for wsi in station_ids:
            url = url_creator(section, month, time_type, wsi)
            download_weather_data(output_dir, url)
            time.sleep(0.5)
            pbar.update(1) # how many times the bar jumps.

    if time_type != "daily":
        for day in days:
            for wsi in station_ids:
                url = url_creator(section, day, time_type, wsi)
                download_weather_data(output_dir, url)
                time.sleep(0.5)
                pbar.update(1) # how many times the bar jumps.

    pbar.close()
    logging.getLogger().setLevel(logging.INFO)


