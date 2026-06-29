import sqlite3
import pandas as pd
from pathlib import Path
from OWM_database import get_connection


def export_historical():
    """Run this once locally to generate the historical CSV from weather.db."""
    db_path = Path(r"C:\Users\nemec\PycharmProjects\Weather_Processing\data\weather.db")
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
    print("Historical export done.")


def update_with_live():
    """Run by GitHub Actions to merge live data into the historical CSV."""
    daily_avg = pd.read_csv("data/daily_avg_historical.csv", parse_dates=['date'])

    conn = get_connection()
    recent = pd.read_sql("""
        SELECT date, AVG(CAST(temp_avg AS FLOAT)) as temp_avg 
        FROM daily 
        WHERE data_richness = 'LARGE'
        GROUP BY date
    """, conn)
    conn.close()

    recent['date'] = pd.to_datetime(recent['date'])

    combined = (pd.concat([daily_avg, recent])
                .drop_duplicates(subset='date', keep='last')
                .sort_values('date')
                .reset_index(drop=True))

    combined.to_csv("data/daily_avg_historical.csv", index=False)
    print(f"Updated: {len(combined)} total rows")

if __name__ == "__main__":
    update_with_live()