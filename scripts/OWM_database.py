# OWM_database.py
# Creates and manages the SQLite database

import sqlite3
import os

# database lives in data/weather.db
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "weather.db")
# create
def get_connection():
    """Returns a connection to the database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    # OWM weather table - sends SQL commands
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS owm_weather (
                                                              id          INTEGER PRIMARY KEY AUTOINCREMENT,
                                                              timestamp   TEXT NOT NULL,
                                                              lat         REAL,
                                                              lon         REAL,
                                                              temperature REAL,
                                                              feels_like  REAL,
                                                              humidity    INTEGER,
                                                              pressure    INTEGER,
                                                              wind_speed  REAL,
                                                              precipitation REAL,
                                                              condition   TEXT,
                                                              city        TEXT
                   )
                   """)

    # OWM pollution table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS owm_pollution (
                                                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                timestamp TEXT NOT NULL,
                                                                lat REAL,
                                                                lon REAL,
                                                                aqi       INTEGER,
                                                                pm2_5 REAL,
                                                                pm10 REAL,
                                                                no2 REAL,
                                                                o3 REAL,
                                                                co REAL,
                                                                so2 REAL
                   )
                   """)
    # open-meteo table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS open_meteo_hourly
                   (
                       id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                       timestamp              TEXT NOT NULL,
                       lat                    REAL,
                       lon                    REAL,
                       temperature            REAL,
                       humidity               INTEGER,
                       wind_speed             REAL,
                       precipitation          REAL,
                       cloud_cover            INTEGER,
                       shortwave_radiation    REAL,
                       weather_code           INTEGER
                   )
                   """)

    conn.commit()
    conn.close()
    print("Tables created!")



# --- insert data ------
# to be continue
def insert_weather(data):
    """Insert one weather snapshot into owm_weather table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT INTO owm_weather
                   (timestamp, lat, lon, temperature, feels_like,
                    humidity, pressure, wind_speed, precipitation, condition, city)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   """, (
                       data["timestamp"], data["lat"], data["lon"],
                       data["temperature"], data["feels_like"],
                       data["humidity"], data["pressure"],
                       data["wind_speed"], data["precipitation"],
                       data["condition"], data["city"]
                   ))
    conn.commit()
    conn.close()


def insert_air_quality(data):
    """Insert one air quality snapshot into owm_pollution table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT INTO owm_pollution
                       (timestamp, lat, lon, aqi, pm2_5, pm10, no2, o3, co, so2)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   """, (
                       data["timestamp"], data["lat"], data["lon"],
                       data["aqi"], data["pm2_5"], data["pm10"],
                       data["no2"], data["o3"], data["co"], data["so2"]
                   ))
    conn.commit()
    conn.close()

# insert for open-meteo historical data
def insert_open_meteo(data):
    """Insert one hourly row into open_meteo_hourly table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO open_meteo_hourly
        (timestamp, lat, lon, temperature, humidity,
         wind_speed, precipitation, cloud_cover,
         shortwave_radiation, weather_code)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["timestamp"], data["lat"], data["lon"],
        data["temperature"], data["humidity"],
        data["wind_speed"], data["precipitation"],
        data["cloud_cover"], data["shortwave_radiation"],
        data["weather_code"]
    ))
    conn.commit()
    conn.close()



def check_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM owm_weather")
    rows = cursor.fetchall()
    print(f"Weather rows: {len(rows)}")
    for row in rows:
        print(row)
    conn.close()




if __name__ == "__main__":
    create_tables()
    check_data()
