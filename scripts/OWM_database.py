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
                                                              timestamp   TEXT NOT NULL,
                                                              temperature REAL,
                                                              feels_like  REAL,
                                                              humidity    INTEGER,
                                                              pressure    INTEGER,
                                                              wind_speed  REAL,
                                                              precipitation REAL,
                                                              condition   TEXT,
                                                              district        TEXT
                   )
                   """)

    # OWM pollution table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS owm_pollution (
                                                                timestamp TEXT NOT NULL,
                                                                aqi       INTEGER,
                                                                pm2_5 REAL,
                                                                pm10 REAL,
                                                                no2 REAL,
                                                                o3 REAL,
                                                                co REAL,
                                                                so2 REAL
                   )
                   """)

    # open-meteo hourly table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS open_meteo_hourly
                   (
                       timestamp              TEXT NOT NULL,
                       temperature            REAL,
                       humidity               INTEGER,
                       wind_speed             REAL,
                       precipitation          REAL,
                       cloud_cover            INTEGER,
                       shortwave_radiation    REAL,
                       weather_code           INTEGER,
                       soil_temperature_0_to_7cm         REAL,
                       soil_temperature_7_to_28cm        REAL,
                       soil_temperature_28_to_100cm      REAL
                   )
                   """)

    # open-meteo daily table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS open_meteo_daily
                   (
                       date                       TEXT NOT NULL,
                       sunrise                    TEXT,
                       sunset                     TEXT,
                       temperature_mean           REAL,
                       temperature_max            REAL,
                       temperature_min            REAL,
                       wind_speed_max             REAL,
                       wind_gusts_max             REAL,
                       wind_direction_dominant    INTEGER,
                       daylight_duration          REAL,
                       sunshine_duration          REAL,
                       precipitation_sum          REAL,
                       rain_sum                   REAL,
                       snowfall_sum               REAL,
                       snowfall_water_equivalent   REAL,
                       precipitation_hours         REAL,
                       cloud_cover_mean            REAL,
                       soil_moisture_0_7cm         REAL,
                       soil_moisture_28_100cm         REAL,
                       soil_moisture_0_100cm         REAL
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
                   (timestamp, temperature, feels_like,
                    humidity, pressure, wind_speed, precipitation, condition, district)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                   """, (
                       data["timestamp"], data["temperature"], data["feels_like"],
                       data["humidity"], data["pressure"],
                       data["wind_speed"], data["precipitation"],
                       data["condition"], data["district"]
                   ))
    conn.commit()
    conn.close()


def insert_air_quality(data):
    """Insert one air quality snapshot into owm_pollution table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT INTO owm_pollution
                       (timestamp, aqi, pm2_5, pm10, no2, o3, co, so2)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   """, (
                       data["timestamp"], data["aqi"], data["pm2_5"], data["pm10"],
                       data["no2"], data["o3"], data["co"], data["so2"]
                   ))
    conn.commit()
    conn.close()

# insert for open-meteo hourly data
def insert_open_meteo_hourly(data):
    """Insert one hourly row into open_meteo_hourly table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO open_meteo_hourly
        (timestamp, temperature, humidity,
         wind_speed, precipitation, cloud_cover,
         shortwave_radiation, weather_code, soil_temperature_0_to_7cm,
         soil_temperature_7_to_28cm, soil_temperature_28_to_100cm)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["timestamp"], data["temperature"], data["humidity"],
        data["wind_speed"], data["precipitation"],
        data["cloud_cover"], data["shortwave_radiation"],
        data["weather_code"], data["soil_temperature_0_to_7cm"],
        data["soil_temperature_7_to_28cm"], data["soil_temperature_28_to_100cm"]
    ))
    conn.commit()
    conn.close()

# insert for open-meteo daily data
def insert_open_meteo_daily(data):
    """Insert one hourly row into open_meteo_dailytable."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO open_meteo_daily
        (date, sunrise, sunset,
         temperature_mean, temperature_max, temperature_min,
         wind_speed_max, wind_gusts_max, wind_direction_dominant, daylight_duration,
        sunshine_duration, precipitation_sum, rain_sum, snowfall_sum,
        snowfall_water_equivalent, precipitation_hours, cloud_cover_mean,
        soil_moisture_0_7cm, soil_moisture_28_100cm, soil_moisture_0_100cm)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["date"], data["sunrise"], data["sunset"],
        data["temperature_mean"], data["temperature_max"],
        data["temperature_min"], data["wind_speed_max"], data["wind_gusts_max"],
        data["wind_direction_dominant"], data["daylight_duration"],
        data["sunshine_duration"], data["precipitation_sum"],
        data["rain_sum"], data["snowfall_sum"], data["snowfall_water_equivalent"],
        data["precipitation_hours"], data["cloud_cover_mean"],
        data["soil_moisture_0_7cm"], data["soil_moisture_28_100cm"],
        data["soil_moisture_0_100cm"]
    ))
    conn.commit()
    conn.close()



# def check_data():
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM owm_weather")
#     rows = cursor.fetchall()
#     print(f"Weather rows: {len(rows)}")
#     for row in rows:
#         print(row)
#     conn.close()




# if __name__ == "__main__":
#     create_tables()
#     check_data()
