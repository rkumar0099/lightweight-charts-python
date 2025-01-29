import pandas as pd
from test_3 import get_filepath

arcs = {
    "5m": 700,
    "10m": 1000,
    "30m": 1800,
    "1h": 2600
}

class Interval:
    def __init__(self, interval):
        self.interval = interval
        self.df_count = 0
        self.cols = ['date', 'open', 'high', 'low', 'close']
        self.data = pd.DataFrame([], columns=self.cols) 

    def add_series(self, series):
        self.data.loc[self.df_count] = series
        self.df_count += 1


def is_arc_bound():
    intervals = {
        5: Interval(5),
        10: Interval(10),
        15: Interval(15),
        30: Interval(30),
        60: Interval(60)
    }
    
    filepath = get_filepath("2025", 1, 7)

    df = pd.read_csv(filepath)
    cols = ['date', 'open', 'high', 'low', 'clise', 'volume', 'quote_volume']
    sub_df = pd.DataFrame([], )
    for i, series in df.iterrows():
        


