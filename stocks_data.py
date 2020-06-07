import requests
import pandas as pd
import pandas_datareader.data as web
from datetime import date
from typing import List


RELEVANT_STOCK_DAILY_STATUS = "Adj Close"

class StocksDataFrame:
    yahoo_df = None
    stocks_count = 0

    @property
    def isValid(self) -> bool:
        return self.yahoo_df is not None

    def fetch_stocks_daily_data(self,
                                tickers_list: List[str],
                                start_date: date,
                                end_date: date = date.today()
                                ) -> pd.DataFrame:
        self.start_date = start_date
        self.end_date = end_date
        try:
            self.yahoo_df = web.get_data_yahoo(tickers_list, start_date, end_date)
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
            raise Exception(f"Error analyzing Yahoo stocks data - {err}")

        self.stocks_count = len(self.yahoo_df.columns)
        return self.yahoo_df


    def _validate_data(self):
        print(f"Data frame nan's = {self.yahoo_df.isnull().sum().sum()} / {len(self.yahoo_df)}")
        self.yahoo_df.dropna()

        df_dates = self.yahoo_df.index
        print(f"Data frame dates: {min(df_dates.astype(str))} - {max(df_dates.astype(str))}")

        columns = self.yahoo_df.columns
        col_vendor = columns.get_level_values(1)
        stocks = list(filter(None, set(col_vendor)))
        print(f"Data Frame stocks - {stocks}")

        col_status = columns.get_level_values(0)
        statuses = list(filter(lambda x: x != 'Date', set(col_status)))
        print(f"Data Frame stocks statuses - {statuses}")
        if RELEVANT_STOCK_DAILY_STATUS not in statuses:
            raise Exception(f"Error - Required stocks' status [{RELEVANT_STOCK_DAILY_STATUS}] is missing in the data")
        print(f"Relevant stocks' status to analyze was found - [RELEVANT_STATUS]")

        columns_by_status = self.yahoo_df.iloc[:, col_status == RELEVANT_STOCK_DAILY_STATUS]
        columns_by_status.columns = [x[1] for x in columns_by_status.columns]

        full_nan_cols = columns_by_status.columns[columns_by_status.isnull().all()].tolist()
        if len(full_nan_cols) > 0:
            raise Exception(f"Error - Missing stocks - {full_nan_cols}")

        return columns_by_status
