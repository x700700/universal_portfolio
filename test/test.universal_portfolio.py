import unittest
import json
from datetime import date
import numpy as np
import matplotlib.pyplot as plt

from helpers import build_debugable_diff_table
from universal_portfolio import UniversalPortfolio

class TestPortfolio(unittest.TestCase):
    universal_portolio = UniversalPortfolio()

    def setUp(self):
        super().setUp()

    def tearDown(self):
        pass


    def test_01_fetch_daily_data(self):
        try:
            df = self.universal_portolio.fetch_stocks_daily_data(['GOOG', 'AAPL', 'MSFT'], date(2018, 1, 1), date(2020, 5, 14))
        except Exception as err:
            self.assertTrue(False, f"Error - {err}")

        with open('./stocks_data.json') as json_file:
            json_stream = json.load(json_file)
        expected = json.loads(json_stream)

        result = df.reset_index().values
        expected = np.array([[x for x in expected['data'][i].values()] for i in range(len(expected['data']))])

        expected_dates = np.array([x[0:-1] for x in expected[:,0]], dtype=np.datetime64)
        result_dates = np.array(result[:,0], dtype=np.datetime64)
        np.testing.assert_equal(expected_dates, result_dates)

        expected_stocks = np.array(expected[:,1:], dtype=float)
        result_stocks = result[:,1:]
        np.testing.assert_almost_equal(expected_stocks, result_stocks, 5)
        print("Stocks data matches expected.")


    def test_02_universal_portfolio_result(self):
        try:
            universal = self.universal_portolio.calculate_universal_portfolio(10)
            trend = universal[:, 1]
        except Exception as err:
            self.assertTrue(False, f"Error - Algo crashed - {err}")

        with open('./universal_portfolio.json') as json_file:
            expected = json.load(json_file)
        comparison_table_for_debug = build_debugable_diff_table(trend, expected)
        np.testing.assert_almost_equal(trend, expected, 5)

        dates = universal[:,0]
        plt.plot_date(dates, trend)
        plt.show()
        print("Universal Portfolio result matches expected.")

if __name__ == '__main__':
    unittest.main()
