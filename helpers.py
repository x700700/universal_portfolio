from datetime import datetime
from typing import List

import pandas as pd
import numpy as np


def ratioanl_array_recursively(arr):
    for i in range(1, len(arr)):
        arr[i] = arr[i] * arr[i - 1]
    return arr

def build_debugable_diff_table(result, expected):
    diff = pd.DataFrame([result, expected]).T
    diff[2] = (diff[0] - diff[1]) * 1000.0
    diff.columns = ['result', 'expected', 'diff (* 1000)']


def from_pd_timestamp_index_to_datetime_list(pd_dates : pd.DatetimeIndex) -> List[datetime]:
    dates = [datetime.utcfromtimestamp(x.tolist() / 1e9) for x in np.array(pd_dates, dtype=np.datetime64)]
    return dates
