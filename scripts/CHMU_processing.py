import logging
import pandas as pd

logger = logging.getLogger(__name__)


class ParsedTableProcessing:
    """
    This class takes a raw tables from the parser and processes them, renames them, and cocatinates them thogheter into
    one continues table.
    """

    def __init__(self, filepath_processed,list_of_processed):
        """
        Args:
            filepath_processed (str): path to the output directory
            list_of_processed (list): list of parsed DataFrames to be concatenated
        """
        self._filepath_processed = filepath_processed
        self._list_of_dfs = list_of_processed

    def concat_tables(self):
        """
        this is our main function in the class, it also calls on the other functions automatically to: reset the index
        after concatinating, renames stations names and enriches them, drops the index( so we the index become the date)
        sort the dates so they are chronologically sorted, and renames all the columns so we know what the measurements
        are in.
        """
        self._concat_df = pd.concat(self._list_of_dfs)
        self._concat_df.reset_index(inplace=True)
        self._concat_df = self._concat_df.sort_index()

        self._station_names()
        self._concat_df.columns.name = None
        self._concat_df = self._concat_df.drop(columns=['index'], errors='ignore')
        self._concat_df = self._concat_df.sort_values(["DATE", "station"])
        self._concat_df = self._concat_df.rename(columns={"DATE": "date"})

        self._rename_columns()
        logger.info("Concatenated %d tables with %s rows", len(self._list_of_dfs), self._concat_df.shape[0])
        return self

    def _rename_columns(self):
        """
        this function renames the columns based on what category they belong to which we detect automatically.
        it also handles timezone localization and date formatting depending on table type.
        """

        DAILY_COLUMNS = {
            "Casmax_00:00": "sunshine_duration",
            "Dmax_00:00": "wind_dir_at_gust",
            "E_AVG": "vapour_pressure_avg",
            "F_AVG": "wind_speed_avg",
            "Fmax_00:00": "wind_gust_max",
            "H_AVG": "humidity_avg",
            "P_AVG": "pressure_avg",
            "SSV_00:00": "sunshine_hours",
            "T_AVG": "temp_avg",
            "API30_06:00": "precip_index_30d",
            "SCE_06:00": "snow_water_equiv",
            "SCEdif_06:00": "snow_water_equiv_change",
            "SNO_06:00": "new_snow_depth",
            "SRA_06:00": "precipitation",
            "SVH_06:00": "total_snow_depth",
            "TMInoc_06:00": "temp_overnight_min",
            "TPM_06:00": "temp_ground_surface",
            "TMA_20:00": "temp_max",
            "TMI_20:00": "temp_min",
            "RGLB_D_SUM": "global_radiation_sum",
            "T05_AVG": "soil_temp_5cm_avg",
            "T10_AVG": "soil_temp_10cm_avg",
            "T20_AVG": "soil_temp_20cm_avg",
            "T50_AVG": "soil_temp_50cm_avg",
            "T100_AVG": "soil_temp_100cm_avg",
            "T05_06:00": "soil_temp_5cm_06AM",
            "T10_06:00": "soil_temp_10cm_06AM",
            "T20_06:00": "soil_temp_20cm_06AM",
            "T50_06:00": "soil_temp_50cm_06AM",
            "T100_06:00": "soil_temp_100cm_06AM",
            "T05_20:00": "soil_temp_5cm_20PM",
            "T10_20:00": "soil_temp_10cm_20PM",
            "T20_20:00": "soil_temp_20cm_20PM",
            "T50_20:00": "soil_temp_50cm_20PM",
            "T100_20:00": "soil_temp_100cm_20PM",
        }

        SYNOPTIC_COLUMNS = {
            "D10": "wind_direction",
            "E": "vapour_pressure",
            "F": "wind_speed",
            "H": "humidity",
            "P": "pressure",
            "T": "temperature",
        }

        HIGH_FREQUENCY_COLUMNS = {

            "E": "vapour_pressure",
            "N": "total_cloud_cover",
            "P_hm": "pressure_station_level",
            "SRA1H": "precipitation_hourly",
            "SSV1H": "sunshine_duration_hourly",
            "Td": "dew_point_temperature",
            "VV": "visibility",
            "W1": "past_weather_1",
            "W2": "past_weather_2",
            "ppp": "pressure_tendency",
            "ww": "present_weather_code",
            "RGLB1H": "global_radiation_hourly",
            "C-MLAv": "mixing_layer_height_avg",
            "C-MLI": "mixing_layer_indicator",
            "T": "temperature",
            "TMA": "temp_max",
            "TMI": "temp_min",
            "TPM": "temp_ground_surface",
            "H": "humidity",
            "P": "pressure",
            "SSV10M": "sunshine_duration_10min",
            "SRA10M": "precipitation_10min",
            "D": "wind_direction",
            "F": "wind_speed",
            "Dprum": "wind_direction_avg",
            "Fprum": "wind_speed_avg",
            "Dmax": "wind_dir_at_gust",
            "Fmax": "wind_gust_max",
            "Casmax": "sunshine_sensor_duration",
            "RGLB10": "global_radiation_10min",
            "T05": "soil_temp_5cm",
            "T10": "soil_temp_10cm",
            "T20": "soil_temp_20cm",
            "T50": "soil_temp_50cm",
            "T100": "soil_temp_100cm",
        }

        if "D10" in self._concat_df.columns:
            self._concat_df = self._concat_df.rename(columns=SYNOPTIC_COLUMNS)
            self._concat_df["date"] = self._concat_df["date"].dt.tz_localize(None)
        elif "SSV1H" in self._concat_df.columns or "SSV10M" in self._concat_df.columns:
            self._concat_df = self._concat_df.rename(columns=HIGH_FREQUENCY_COLUMNS)
        else:
            self._concat_df = self._concat_df.rename(columns=DAILY_COLUMNS)
            self._concat_df["date"] = self._concat_df["date"].dt.date

        return self

    def _station_names(self):
        """
        a simple function which maps the WSI codes to their station names and it also creates a new column which
        says how data rich a stations is.
        """

        STATION_NAMES = {
            "0-20000-0-11518": "Praha-Ruzyne",
            "0-20000-0-11519": "Praha-Karlov",
            "0-20000-0-11520": "Praha-Libus",
            "0-20000-0-11567": "Praha-Kbely",
            "0-203-0-10904013001": "Praha-Komorany",
            "0-203-0-11105048001": "Praha-Zadni Kopanina",
            "0-203-0-11201020001": "Praha-Vinohrady",
            "0-203-0-11201020003": "Praha-Chodov",
            "0-203-0-11201024001": "Praha-Brevnov",
            "0-203-0-11202007001": "Praha-Suchdol",
            "0-203-0-11514": "Praha-Klementinum",
            "0-203-0-11515": "Praha-Klementinum II",
        }

        RICHNESS = {
            "Praha-Ruzyne": "LARGE",
            "Praha-Karlov": "LARGE",
            "Praha-Libus" : "LARGE",
            "Praha-Kbely" : "LARGE",
            "Praha-Komorany" : "MEDIUM",
            "Praha-Zadni Kopanina" : "MINIMUM",
            "Praha-Vinohrady" : "MEDIUM",
            "Praha-Chodov" : "MINIMUM",
            "Praha-Brevnov" : "MINIMUM",
            "Praha-Suchdol": "MINIMUM",
            "Praha-Klementinum" : "MEDIUM",
            "Praha-Klementinum II" : "MINIMUM",
        }

        self._concat_df = self._concat_df.rename(columns={"STATION": "station"})
        self._concat_df["station"] = self._concat_df["station"].map(STATION_NAMES)
        self._concat_df["data_richness"] = self._concat_df["station"].map(RICHNESS)

        return self