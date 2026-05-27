# parsing data for OWM and open-meteo
# import packages
from datetime import datetime, timezone, date, timedelta

import pandas as pd

DAILY_COLUMNS = {
            "time": "date",
            "temperature_2m_mean": "temperature_mean",
            "temperature_2m_max": "temperature_max",
            "temperature_2m_min": "temperature_min",
            "wind_speed_10m_max": "wind_speed_max",
            "wind_gusts_10m_max": "wind_gusts_max",
            "wind_direction_10m_dominant": "wind_direction_dominant",
            "snowfall_water_equivalent_sum": "snowfall_water_equivalent",
            "soil_moisture_0_to_7cm_mean": "soil_moisture_0_7cm",
            "soil_moisture_28_to_100cm_mean": "soil_moisture_28_100cm",
            "soil_moisture_0_to_100cm_mean": "soil_moisture_0_100cm",
        }

# parsing for both weather and air quality for OWM
class OWMParser:
    def __init__(self, raw):
        self._raw = raw

    def parse_weather(self):
        """Parse OWM weather response into clean flat dictionary."""
        main = self._raw.get("main", {})
        wind = self._raw.get("wind", {})
        weather = self._raw.get("weather", [{}])
        
        return {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": main.get("temp"),
            "feels_like": main.get("feels_like"),
            "humidity": main.get("humidity"),
            "pressure": main.get("pressure"),
            "wind_speed": wind.get("speed"),
            "precipitation": self._raw.get("rain", {}).get("1h", 0.0),
            "condition": weather[0].get("description"),
            "district": self._raw.get("name"),
        }

    def parse_air_quality(self):
        """Parse OWM air quality response into clean flat dictionary."""
        components = self._raw.get("list", [{}])[0].get("components", {})
        main = self._raw.get("list", [{}])[0].get("main", {})

        return {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "aqi": main.get("aqi"),
            "pm2_5": components.get("pm2_5"),
            "pm10": components.get("pm10"),
            "no2": components.get("no2"),
            "o3": components.get("o3"),
            "co": components.get("co"),
            "so2": components.get("so2"),
        }


class OpenMeteoParser:
    def __init__(self, raw):
        self._raw = raw

    def parse_hourly(self):
        """Parse hourly Open-Meteo response into clean dictionary."""
        current = self._raw.get("current", {})
        return {
            "timestamp": pd.to_datetime(current.get("time")).strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
            "precipitation": current.get("precipitation"),
            "cloud_cover": current.get("cloud_cover"),
            "shortwave_radiation": current.get("shortwave_radiation"),
            "weather_code": current.get("weather_code"),
            "soil_temperature_0_to_7cm": current.get("soil_temperature_0_to_7cm"),
            "soil_temperature_7_to_28cm": current.get("soil_temperature_7_to_28cm"),
            "soil_temperature_28_to_100cm": current.get("soil_temperature_28_to_100cm"),
        }

    def parse_daily(self):
        """Parse daily Open-Meteo response into clean dictionary."""

        daily_table = (
            pd.DataFrame(data=self._raw.get("daily", {}))
            .rename(columns=DAILY_COLUMNS)
            .assign(date=lambda x: pd.to_datetime(x["date"]).dt.date)
            .assign(sunrise=lambda x: pd.to_datetime(x["sunrise"]))
            .assign(sunset=lambda x: pd.to_datetime(x["sunset"]))
        ).iloc[0]

        return daily_table

    def parse_hourly_historical(self):
        """
        Parser the historical part of our data, renames some of the columns and also changes the time date.
        """

        historical_hourly_table = (
            pd.DataFrame(data = self._raw.get("hourly",{}))
            .rename(columns = {"time":"timestamp",
                               "temperature_2m" : "temperature",
                               "relative_humidity_2m":"humidity",
                               "wind_speed_10m":"wind_speed"})
            .assign(timestamp = lambda x: pd.to_datetime(x["timestamp"]))
            .assign(timestamp=lambda x: pd.to_datetime(x["timestamp"]))
            .sort_values("timestamp", ascending=False)
        )
        return historical_hourly_table

    def parse_daily_historical(self):
        """
        Parse historical daily data, fixes the date time variables to be pandas data time, and also renames
        the columns for clarity
        """

        historical_daily_table = (
            pd.DataFrame(data = self._raw.get("daily",{}))
            .rename(columns = DAILY_COLUMNS)
            .assign(date = lambda x: pd.to_datetime(x["date"]).dt.date)
            .assign(sunrise = lambda x: pd.to_datetime(x["sunrise"]))
            .assign(sunset = lambda x: pd.to_datetime(x["sunset"]))
            .assign(date=lambda x: pd.to_datetime(x["date"]).dt.date)
            .sort_values("date", ascending=False)
        )

        return historical_daily_table



