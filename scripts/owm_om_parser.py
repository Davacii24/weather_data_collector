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

    # add to OpenMeteoParser class in owm_om_parser.py:

    def parse_hourly_historical(self):
        """Parse historical hourly response - returns list of dicts."""
        hourly = self._raw.get("hourly", {})
        rows = []
        for i in range(len(hourly["time"])):
            rows.append({
                "timestamp": hourly["time"][i],
                "temperature": hourly["temperature_2m"][i],
                "humidity": hourly["relative_humidity_2m"][i],
                "wind_speed": hourly["wind_speed_10m"][i],
                "precipitation": hourly["precipitation"][i],
                "cloud_cover": hourly["cloud_cover"][i],
                "shortwave_radiation": hourly["shortwave_radiation"][i],
                "weather_code": hourly["weather_code"][i],
                "soil_temperature_0_to_7cm": hourly["soil_temperature_0_to_7cm"][i],
            })
        return rows

    def parse_daily_historical(self):
        """Parse historical daily response - returns list of dicts."""
        daily = self._raw.get("daily", {})
        rows = []
        for i in range(len(daily["time"])):
            rows.append({
                "date": daily["time"][i],
                "sunrise": daily["sunrise"][i],
                "sunset": daily["sunset"][i],
                "temperature_mean": daily["temperature_2m_mean"][i],
                "temperature_max": daily["temperature_2m_max"][i],
                "temperature_min": daily["temperature_2m_min"][i],
                "wind_speed_max": daily["wind_speed_10m_max"][i],
                "wind_gusts_max": daily["wind_gusts_10m_max"][i],
                "wind_direction_dominant": daily["wind_direction_10m_dominant"][i],
                "daylight_duration": daily["daylight_duration"][i],
                "sunshine_duration": daily["sunshine_duration"][i],
                "precipitation_sum": daily["precipitation_sum"][i],
                "rain_sum": daily["rain_sum"][i],
                "snowfall_sum": daily["snowfall_sum"][i],
                "snowfall_water_equivalent": daily["snowfall_water_equivalent_sum"][i],
                "precipitation_hours": daily["precipitation_hours"][i],
                "cloud_cover_mean": daily["cloud_cover_mean"][i],
                "soil_moisture_0_7cm": daily["soil_moisture_0_to_7cm_mean"][i],
                "soil_moisture_28_100cm": daily["soil_moisture_28_to_100cm_mean"][i],
                "soil_moisture_0_100cm": daily["soil_moisture_0_to_100cm_mean"][i],
            })
        return rows


