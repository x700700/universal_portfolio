import pandas as pd


def ratioanl_array_recursively(arr):
    for i in range(1, len(arr)):
        arr[i] = arr[i] * arr[i - 1]
    return arr

def build_debugable_diff_table(result, expected):
    diff = pd.DataFrame([result, expected]).T
    diff[2] = (diff[0] - diff[1]) * 1000.0
    diff.columns = ['result', 'expected', 'diff (* 1000)']
