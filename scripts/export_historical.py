import sqlite3
import pandas as pd
from pathlib import Path

db_path = Path("data/weather.db")
conn = sqlite3.connect(str(db_path))
daily = pd.read_sql("SELECT date, temp_avg, temp_max, temp_min, station FROM daily", conn)
conn.close()

daily['date'] = pd.to_datetime(daily['date'])
daily['temp_avg'] = pd.to_numeric(daily['temp_avg'], errors='coerce')
daily['temp_max'] = pd.to_numeric(daily['temp_max'], errors='coerce')
daily['temp_min'] = pd.to_numeric(daily['temp_min'], errors='coerce')

daily_avg = daily.groupby('date')['temp_avg'].mean().reset_index()

daily_avg.to_csv("data/daily_avg_historical.csv", index=False)

daily['period'] = (daily['date'].dt.year // 20) * 20
stations = daily.groupby('period')['station'].nunique()
years = daily.groupby('period')['date'].apply(lambda x: x.dt.year.nunique())

hot = (daily[daily['temp_max'] > 30].groupby('period')['temp_max'].count() / stations / years).dropna()
cold = (daily[daily['temp_min'] < 0].groupby('period')['temp_min'].count() / stations / years).dropna()

extremes = pd.DataFrame({'hot': hot, 'cold': cold}).fillna(0)
extremes.to_csv("data/extremes_by_period.csv")

print("Done! Check data/ folder")