import operator as op
import json
import pandas as pd

class CHMUAutoParser:
    def __init__(self,filepath_raw, filepath_processed):
        self.file_path_raw = filepath_raw
        self.file_path_processed = filepath_processed

    def load(self):
        with open(self.file_path_raw,'r') as f:
            self._raw_data = json.load(f)

        v_type = "VTYPE"
        self._v_type = op.contains(self._raw_data["data"]["data"]["header"], v_type)
        self._station_ids = self._raw_data["data"]["data"]["values"][0][0]

        return self

    def parse(self):
        if self._v_type:
            return self._parse_daily_data()
        else:
            return self._parse_highfreq_data()

    def _parse_daily_data(self):
        print("Parsing daily data...")

        column_names = str.split(self._raw_data["data"]["data"]["header"],sep = ",")

        df = (
            pd.DataFrame(data = self._raw_data["data"]["data"]["values"] , columns = column_names)
            .assign(ELEMENT_VTYPE = lambda x: x["ELEMENT"] + "_" + x["VTYPE"])
            .drop(columns=["FLAG","QUALITY"])
            )

        daily_table = (
            df[df["DT"].str.contains("T00:00")]
            .pivot(index="DT",columns= ["ELEMENT_VTYPE"],values="VAL")
            )
        daily_table.index = pd.to_datetime(daily_table.index).date

        six_am_table = (
            df[df["DT"].str.contains("T06:00")]
            .pivot(index="DT", columns=["ELEMENT_VTYPE"], values="VAL")
            .drop(columns=["VY_06:00","D10_06:00" ,"E_06:00",
                           "F_06:00","H_06:00", "P_06:00","T_06:00"],errors="ignore")

            )
        six_am_table.index = pd.to_datetime(six_am_table.index).date

        night_table = (
            df[df["DT"].str.contains("T20:00")]
            .pivot(index="DT", columns=["ELEMENT_VTYPE"], values="VAL")
            .drop(columns= ["D10_20:00" ,"E_20:00","F_20:00","H_20:00",
                            "P_20:00","T_20:00"],errors="ignore")
            )
        night_table.index = pd.to_datetime(night_table.index).date

        daily_table = (
            daily_table
            .join(six_am_table)
            .join(night_table)
            .reset_index()
            .rename(columns={"index": "DATE"})
            .assign(DATE=lambda x: pd.to_datetime(x["DATE"]))
            .assign(year = lambda x: x['DATE'].dt.year)
            .assign(month = lambda x: x['DATE'].dt.month)
            .assign(weekday_name = lambda x: x['DATE'].dt.day_name())
            .assign(is_weekend = lambda x: (x['DATE'].dt.dayofweek == 5) | (x['DATE'].dt.dayofweek == 6))
            .sort_values('DATE', ascending=True)
            .assign(STATION = self._station_ids)
        )

        ################################################################################################
        core = ["D10", "E", "F", "H", "P", "T"]

        night_t = (
            df[df["DT"].str.contains("T20:00")]
            .pivot(index="DT", columns=["ELEMENT_VTYPE"], values="VAL")
        )
        night_t.columns = night_t.columns.str.replace("_20:00", "")
        night_t = night_t[night_t.columns.intersection(core)]

        morning_t = (
            df[df["DT"].str.contains("T06:00")]
            .pivot(index="DT", columns=["ELEMENT_VTYPE"], values="VAL")
        )
        morning_t.columns = morning_t.columns.str.replace("_06:00", "")
        morning_t = morning_t[morning_t.columns.intersection(core)]

        midday_t = (
            df[df["DT"].str.contains("T13:00")]
            .pivot(index="DT", columns=["ELEMENT_VTYPE"], values="VAL")
        )
        midday_t.columns = midday_t.columns.str.replace("_13:00", "")
        midday_t = midday_t[midday_t.columns.intersection(core)]

        daily_series_table = (
            pd.concat([night_t, midday_t, morning_t])
            .reset_index()
            .rename(columns={"DT": "DATE"})
            .assign(DATE=lambda x: pd.to_datetime(x["DATE"]))
            .assign(year = lambda x: x['DATE'].dt.year)
            .assign(month=lambda x: x['DATE'].dt.month)
            .assign(weekday_name=lambda x: x['DATE'].dt.day_name())
            .assign(is_weekend=lambda x: (x['DATE'].dt.dayofweek == 5) | (x['DATE'].dt.dayofweek == 6))
            .assign(STATION=self._station_ids)
        )
        daily_series_table = daily_series_table.sort_index()

        return daily_table, daily_series_table

    def _parse_highfreq_data(self):
        print("Parsing high frequency data")