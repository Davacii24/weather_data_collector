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

def url_creator(section,time_type,date,WSI_code):

    base = "https://opendata.chmi.cz/meteorology/climate/"
    section = section
    time_type = f"{time_type}"
    WSI_code = f"{WSI_code}"
    date = f"{date}"

    if section == "now":
        if time_type == "10m":
            url = f"{base}{section}/data/{time_type}-{WSI_code}-{date}.json"
    else:
        logger.warning(f"the format was misspecified")
        return ""

    logger.info(f"url created: {url}")
    return url

