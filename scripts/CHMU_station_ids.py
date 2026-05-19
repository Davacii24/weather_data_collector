from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def station_ids(df):
    """
    this function will extract the station ids from a dataframe

    Args:
        df (pd.DataFrame): the dataframe
    Returns:
        prague_station_ids_all, even the ones that we close already
        for historical data analysis purposes

        prague_station_ids_current : return just the active stations for downloading the data
        which is actually downloadable

    """
    df = df.copy()
    # we of course pase the data frame.
    df["END_DATE"] = pd.to_datetime(df["END_DATE"],errors="coerce",format="mixed",dayfirst=True)

    # We create the filters for the data frame
    names = df["FULL_NAME"].str.contains("Praha",regex=True)
    date = df["END_DATE"] > pd.Timestamp.now(tz="utc")

    prague_station_ids_all = df[names] # all ids, even historical ones
    prague_station_ids_current = df[names & date] # current ids

    # we save their WIGOs Station Identifier
    WSI_all = prague_station_ids_all["WSI"].drop_duplicates().to_list()
    WSI_current = prague_station_ids_current["WSI"].to_list()

    logger.info("station IDs created  %s: ", WSI_current)
    return WSI_all, WSI_current

URL_PATTERNS = {
    ("now","10m"): "{base}/now/data/10m-{wsi}-{date}.json",
    ("now","1h") : "{base}/now/data/1h-{wsi}-{date}.json",

    ("recent","10min") : "{base}/recent/data/10min/10m-{wsi}-{date}.json",
    ("recent","1hour") : "{base}/recent/data/1hour/1h-{wsi}-{date}.json",
    ("recent","daily") : "{base}/recent/data/daily/dly-{wsi}-{date}.json",

    ("historical","daily") : "{base}/historical/data/daily/dly-{wsi}.json",
    ("historical","10min") : "{base}/historical/data/10min/{YEAR}/10m-{wsi}-{date}.json",

    ("recent","1hour_old") : "{base}/recent/data/1hour/{MM}/1h-{wsi}-{date}.json",
    ("recent","10min_old") : "{base}/recent/data/10min/{MM}/10m-{wsi}-{date}.json",
    ("recent", "daily_old"): "{base}/recent/data/daily/{MM}/dly-{wsi}-{date}.json",
}

def url_creator(section,date,time_type,WSI_code):
    """
    this function will create the url from the section and date, which is used to download the data
    this function also automatically handles if the date is in the past year, and creates the correct
    url accordingly.

    Args:
        section (string): the section names : now, recent, historical
        date (string): the date of the data : YYYY-MM-DD like 20200506 for daily and YYYY-MM for monthly(202107)
        time_type (string): the time type of the data which could be from 10 minutes to yearly data
        WSI_code (string): the WSI code of the station

    Returns:
          returns the URL created, or if error return the needed patterns.
    """

    try:
        url = URL_PATTERNS[(section,time_type)]
    except KeyError:
        logger.error(f"Invalid arguments, {section},{time_type} must be one of {list(URL_PATTERNS.keys())}")
        return

    base = "https://opendata.chmi.cz/meteorology/climate"

    todays_month = datetime.today().month

    if section == "historical" and time_type == "10min":
        url = URL_PATTERNS[("historical","10min")]
        url = url.format(base=base, YEAR = date[0:4], wsi=WSI_code, date=date[0:6])
        logger.info("URL created for %s [%s/%s]: %s", WSI_code, section, time_type, url)
        return url
    elif section == "historical":
        url = URL_PATTERNS[("historical","daily")]
        url = url.format(base=base,wsi=WSI_code)
        logger.info("URL created for %s [%s/%s]: %s", WSI_code, section, time_type, url)
        return url
    elif int(date[4:6]) != todays_month:
        date = date[0:6]
        url = URL_PATTERNS[("recent",f"{time_type}_old")]
        url = url.format(base=base, MM=date[4:6], wsi=WSI_code, date=date)
        logger.info("URL created for %s [%s/%s]: %s", WSI_code, section, time_type, url)
        return url
    else:
        url = url.format(base=base,wsi=WSI_code,date=date)
        logger.info("URL created for %s [%s/%s]: %s", WSI_code, section, time_type, url)
        return url


