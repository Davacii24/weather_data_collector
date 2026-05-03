# GOAL FOR TODAY : 1. Make downloading from python
#                : 2. Basic Parsing

import requests
from pathlib import Path
import json
import logging

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
        Returns a nice messege when succsefull
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


