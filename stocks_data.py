import requests
from datetime import date
from typing import List

import pandas as pd
import pandas_datareader.data as web

from helpers import from_pd_timestamp_index_to_datetime_list


RELEVANT_DAILY_STATUS = "Adj Close"

class StocksDataFrame:
    yahoo_df = None
    stocks = []
    stocks_count = 0
    dates = []

    @property
    def isValid(self) -> bool:
        return self.yahoo_df is not None

    def fetch_stocks_daily_data(self,
                                tickers: List[str],
                                start_date: date,
                                end_date: date = date.today()
                                ) -> pd.DataFrame:
        self.start_date = start_date
        self.end_date = end_date
        try:
            self.yahoo_df = web.get_data_yahoo(tickers, start_date, end_date)
        except Exception as err:
            self.yahoo_df = None
            raise Exception(f"Error reading Yahoo stocks data - {err}")
        # Close pandas_datareader session:
        session = requests.Session()
        session.close()
        try:
            self.yahoo_df = self._validate_data()
        except Exception as err:
            self.yahoo_df = None
            raise Exception(f"Error analyzing Yahoo stocks data frame - {err}")

        self.stocks_count = len(self.yahoo_df.columns)
        return self.yahoo_df


    def _validate_data(self):
        print(f"Data frame nan's = {self.yahoo_df.isnull().sum().sum()} / {len(self.yahoo_df)}")
        self.yahoo_df.dropna()

        df_dates = self.yahoo_df.index
        print(f"Data frame dates: {min(df_dates.astype(str))} - {max(df_dates.astype(str))}")

        columns = self.yahoo_df.columns
        col_vendor = columns.get_level_values(1)
        self.stocks = list(set(col_vendor))
        print(f"Data Frame stocks - {self.stocks}")

        col_status = columns.get_level_values(0)
        statuses = list(filter(lambda x: x != 'Date', set(col_status)))
        print(f"Data Frame stocks statuses - {statuses}")
        if RELEVANT_DAILY_STATUS not in statuses:
            raise Exception(f"Error - data is missing relevant stocks' daily status [{RELEVANT_DAILY_STATUS}]")
        print(f"Relevant daily status was found - [{RELEVANT_DAILY_STATUS}]")

        columns_by_status = self.yahoo_df.iloc[:, col_status == RELEVANT_DAILY_STATUS]
        columns_by_status.columns = [x[1] for x in columns_by_status.columns]
        self.yahoo_df = columns_by_status

        full_nan_cols = columns_by_status.columns[columns_by_status.isnull().all()].tolist()
        if len(full_nan_cols) > 0:
            raise Exception(f"Error - Missing stocks - {full_nan_cols}")

        self.dates = from_pd_timestamp_index_to_datetime_list(self.yahoo_df.index)

        return columns_by_status
