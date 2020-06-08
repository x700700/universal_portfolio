import numpy as np
from datetime import date
from typing import List

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from helpers import ratioanl_array_recursively
from stocks_data import StocksDataFrame


PLT_X_AXIS_DATES_NUM = 6

class UniversalPortfolio(StocksDataFrame):
    universal = None
    plt = None

    def calculate_universal_portfolio(self, portfolio_quantization: int = 20) -> List[float]:
        self._validate_universal_parms(portfolio_quantization)
        try:
            (weights, weights_even) = self._calculate_weights(portfolio_quantization)
            ratios = self._calculate_ratios()
            trend = [1.0]
            previous_day = np.ones(len(weights))
            i_trend = 1
            for r in ratios:
                day = sum(((weights.T * previous_day).T * r).T)
                previous_day = day
                if i_trend == 1:
                    b = weights_even
                else:
                    b = sum((weights.T * current_day).T) / np.sum(current_day)
                trend.append(sum(b * r))
                current_day = day
                i_trend += 1
            trend = ratioanl_array_recursively(trend)
            self.universal = np.vstack((self.dates, trend)).T
            return self.universal
        except Exception as err:
            raise Exception(f"Error during porfolio calculations - {err}")

    def get_plot(self):
        if self.universal is None:
            raise Exception("Universal portfolio was not calculated. Call calculate_universal_portfolio() first.")
        trend = self.universal[:, 1]
        dates = self.universal[:, 0]
        plt.plot_date(dates, trend, linestyle='-', markersize=0.0)
        plt.title(f'Trend for stocks: {self.stocks}')
        ax = plt.gca()
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        ax.xaxis.set_major_locator(plt.MaxNLocator(PLT_X_AXIS_DATES_NUM))
        # No good, distort the x axis:
        # x_dates = ax.get_xticks()[0:PLT_X_AXIS_DATES_NUM]
        # x_dates[-1] = dates[-1].toordinal()
        # ax.set_xticks(x_dates)
        self.plt = plt
        return self.plt

    # ==================================================================================================
    # helpers functions:
    # ==================================================================================================

    def _validate_universal_parms(self, portfolio_quantization: int):
        if portfolio_quantization < 1 or portfolio_quantization > 100:
            raise Exception("Error - portfolio_quantization must be between 1-100")
        if not self.isValid:
            raise Exception("Error - benchmark data is invalid")
        if len(self.yahoo_df.columns) == 0:
            raise Exception("Error - stocks table is empty")
        if len(self.yahoo_df) == 0:
            raise Exception("Error - benchmark data is empty")

    def _calculate_weights(self, quant: int):
        # Build weights array
        #   E.g. for 3 stocks when quant=2:
        #   [[.5, .5, .0], [.5, 0, .5], [0, 0, 1], [0, .5, .5], ....]
        #
        indices = np.indices([quant+1 for _ in range(self.stocks_count)])
        chosen_indices = indices.sum(axis=0) == quant
        weights = indices[:, chosen_indices].T / quant
        weights_even = np.ones(self.stocks_count) / self.stocks_count
        return (weights, weights_even)

    def _calculate_ratios(self):
        tomorrow = self.yahoo_df.to_numpy()
        today = np.insert(tomorrow, 0, tomorrow[0], axis=0)[0:-1]
        ratios = tomorrow / today
        return ratios[1:]


if __name__ == '__main__':
    start_date = date(2018, 1, 1)
    end_date = date(2020, 6, 30)
    tickers = ["GOOG", "AAPL", "MSFT", "AMZN", "FB"]
    n = 2

    upo = UniversalPortfolio()
    df = upo.fetch_stocks_daily_data(tickers, start_date, end_date)
    # print(df.head())
    universal = upo.calculate_universal_portfolio(n)
    plt = upo.get_plot()
    plt.show()
