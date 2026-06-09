import pandas as pd
from scripts.OWM_database import get_connection
import streamlit as st
conn = get_connection()  # you already have this function

query = """
    SELECT * FROM minute
    WHERE (station, date) IN (
    SELECT station, MAX(date)
    FROM minute
    WHERE data_richness = "LARGE"
    GROUP BY station
    )
"""

df = (pd.read_sql_query(query, conn)
      .assign(date = lambda x:  pd.to_datetime(x['date'])
                                .dt.tz_localize("UTC")
                                .dt.tz_convert("Europe/Prague")
                                .dt.tz_localize(None))
      )


print(df.head(10))