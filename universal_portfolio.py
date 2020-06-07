import numpy as np
import matplotlib.pyplot as plt
from datetime import date, datetime
from typing import List

from helpers import ratioanl_array_recursively
from stocks_data import StocksDataFrame

class UniversalPortfolio(StocksDataFrame):
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
                current_day = day # to align ratios and days arrays
                i_trend += 1
            trend = ratioanl_array_recursively(trend)

            dates = [datetime.utcfromtimestamp(x.tolist()/1e9) for x in np.array(self.yahoo_df.index, dtype=np.datetime64)]
            trend = np.vstack((dates, trend)).T
            return trend
        except Exception as err:
            raise Exception(f"Error during porfolio calculations - {err}")

    # ==================================================================================================
    # helpers functions:
    # ==================================================================================================

    def _validate_universal_parms(self, portfolio_quantization: int):
        if not self.isValid:
            raise Exception("Error - benchmark data is invalid")
        if len(self.yahoo_df) == 0:
            raise Exception("Error - benchmark data is empty")
        if portfolio_quantization < 1 or portfolio_quantization > 100:
            raise Exception("Error - quant must be between 1-100")
        if len(self.yahoo_df.columns) == 0:
            raise Exception("Error - stocks table is empty")

    def _calculate_weights(self, quant: int):
        # Build weights array
        #   E.g. for 3 stocks when quant=2:
        #   [[.5, .5, .0], [.5, 0, .5], [0, 0, 1], [0, .5, .5], ....]
        #
        indices = np.indices([quant+1 for _ in range(self.stocks_count)])
        chosen_indices = indices.sum(axis=0) == quant
        weights = (indices[:, chosen_indices].T) / quant
        weights_even = np.ones(self.stocks_count) / self.stocks_count
        return (weights, weights_even)

    def _calculate_ratios(self):
        tomorrow = self.yahoo_df.to_numpy()
        today = np.insert(tomorrow, 0, tomorrow[0], axis=0)[0:-1]
        ratios = tomorrow / today
        return ratios[1:]


if __name__ == '__main__':
    upo = UniversalPortfolio()
    df = upo.fetch_stocks_daily_data(["GOOG", "AAPL", "MSFT"], date(2018, 1, 1), date(2019, 12, 31))
    print(df.head())
    universal = upo.calculate_universal_portfolio(10)
    trend = universal[:, 1]
    dates = universal[:, 0]
    plt.plot_date(dates, trend)
    plt.show()
