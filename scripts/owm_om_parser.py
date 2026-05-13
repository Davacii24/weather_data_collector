# parsing data for OWM and open-meteo
# import packages
from datetime import datetime, timezone, date, timedelta

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
            "city": self._raw.get("name"),
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
            "timestamp": current.get("time"),
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
        daily = self._raw.get("daily", {})
        return {
            "date": daily.get("time", [None])[0],
            "lat": self._raw.get("latitude"),
            "lon": self._raw.get("longitude"),
            "sunrise": daily.get("sunrise", [None])[0],
            "sunset": daily.get("sunset", [None])[0],
            "temperature_mean": daily.get("temperature_2m_mean", [None])[0],
            "temperature_max": daily.get("temperature_2m_max", [None])[0],
            "temperature_min": daily.get("temperature_2m_min", [None])[0],
            "wind_speed_max": daily.get("wind_speed_10m_max", [None])[0],
            "wind_gusts_max": daily.get("wind_gusts_10m_max", [None])[0],
            "wind_direction_dominant": daily.get("wind_direction_10m_dominant", [None])[0],
            "daylight_duration": daily.get("daylight_duration", [None])[0],
            "sunshine_duration": daily.get("sunshine_duration", [None])[0],
            "precipitation_sum": daily.get("precipitation_sum", [None])[0],
            "rain_sum": daily.get("rain_sum", [None])[0],
            "snowfall_sum": daily.get("snowfall_sum", [None])[0],
            "snowfall_water_equivalent": daily.get("snowfall_water_equivalent_sum", [None])[0],
            "precipitation_hours": daily.get("precipitation_hours", [None])[0],
            "cloud_cover_mean": daily.get("cloud_cover_mean", [None])[0],
            "soil_moisture_0_7cm": daily.get("soil_moisture_0_to_7cm_mean", [None])[0],
            "soil_moisture_28_100cm": daily.get("soil_moisture_28_to_100cm_mean", [None])[0],
            "soil_moisture_0_100cm": daily.get("soil_moisture_0_to_100cm_mean", [None])[0],
        }


