import sqlite3
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
logger = logging.getLogger(__name__)

LIVE_PATH = "data/weather_live.db"
MAIN_PATH = "data/weather.db"

TABLES = {
    "minute": "date",
    "hourly": "date",
    "daily": "date",
    "synoptic": "date",
    "open_meteo_hourly": "timestamp",
    "open_meteo_daily": "date",
    "owm_weather": "timestamp",
    "owm_pollution": "timestamp",
}

live = sqlite3.connect(LIVE_PATH)
main = sqlite3.connect(MAIN_PATH)

for table, date_col in TABLES.items():
    try:
        df_live = pd.read_sql(f"SELECT * FROM {table}", live)
    except Exception:
        logger.warning("Table %s not found in live db, skipping", table)
        continue

    try:
        df_main = pd.read_sql(f"SELECT * FROM {table}", main)
    except Exception:
        logger.info("Table %s not found in main db, creating", table)
        df_live.to_sql(table, main, index=False)
        logger.info("%s: added %d rows (new table)", table, len(df_live))
        continue

    combined = pd.concat([df_main, df_live], ignore_index=True)
    before = len(combined)
    combined = combined.drop_duplicates()
    after = len(combined)

    combined.to_sql(table, main, if_exists="replace", index=False)
    new_rows = after - len(df_main)
    logger.info("%s: %d existing + %d new → %d total (%d duplicates removed)",
                table, len(df_main), len(df_live), after, before - after)

live.close()
main.close()
logger.info("Merge complete")