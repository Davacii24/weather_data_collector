from datetime import datetime
import pandas as pd
import logging

#df = pd.read_csv("../data/raw_data/meta1.csv")
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

    logger.info("station ideas created  %s: %s", WSI_all,WSI_current)
    return WSI_all, WSI_current


# FINISH THE URL_CREATOR.

URL_PATTERNS = {
    ("now","10m"): "{base}/now/data/10m-{wsi}-{date}.json",
    ("now","1h") : "{base}/now/data/1h-{wsi}-{date}.json",
    ###

    ("recent","1hour_old") : "{base}/recent/data/1hour/{MM}/1h-{wsi}-{date}.json",
    ("recent","10min_old") : "{base}/recent/data/10min/{MM}/10m-{wsi}-{date}.json",
    ("recent","10min") : "{base}/recent/data/10min/10m-{wsi}-{date}.json",
    ("recent","1hour") : "{base}/recent/data/1hour/1h-{wsi}-{date}.json",
    ("recent","daily") : "{base}/recent/data/daily/dly-{wsi}-{date}.json",
    ("recent","daily_old") : "{base}/recent/data/daily/{MM}/dly-{wsi}-{date}.json",

    ###
    ("historical","monthly") : "{base}/historical/data/monthly/mly-{wsi}.json",
    ####

    ("historical_csv","10m") : "{base}/historical_csv/data/10m-{wsi}-{date}.csv",
    ("historical_csv","1h") : "{base}/historical_csv/data/1h-{wsi}-{date}.csv",
    ("historical_csv","daily") : "{base}/historical_csv/data/daily-{wsi}-{date}.csv",
    #("historical_csv","monthly") : "{base}/historical_csv/data/monthly-{wsi}-{date}.csv",
    ("historical_csv","yearly") : "{base}/historical_csv/data/yearly-{wsi}-{date}.csv",
}

def url_creator(section,date,time_type,WSI_code):
    """
    this function will create the url from the section and date, which is used to download the data

    Args:
        section (string): the section names : now, recent, historical_csv
        date (string): the date of the data : its must in a format YYYY-MM-DD like 2020506
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
    if int(date[4:6]) != todays_month:
        if time_type=="daily":
            # Past-month files aggregate all data for one month -> YYYYMM format
            date = date[0:6]
            url = URL_PATTERNS[("recent","daily_old")]
            url = url.format(base=base, MM = date[4:6] ,wsi=WSI_code,date=date)
        elif time_type=="10min":
            date = date[0:6]
            url = URL_PATTERNS[("recent","10min_old")]
            url = url.format(base=base, MM=date[4:6], wsi=WSI_code, date=date)
        elif time_type=="1hour":
            date = date[0:6]
            url = URL_PATTERNS[("recent","1hour_old")]
            url = url.format(base=base, MM=date[4:6], wsi=WSI_code, date=date)
    else:
        url = url.format(base=base,wsi=WSI_code,date=date)

    logger.info(f"url created: {url}")
    return url

