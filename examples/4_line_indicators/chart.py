import time
from time import sleep
import pandas as pd
from test_3 import get_date
from test_3 import ChartLocal
from lightweight_charts import Chart
from lightweight_charts.abstract import Line

'''
date = get_date(time.time()*1000)
time_tokens = date.split(' ')[1].split(":")
time_str = time_tokens[0]+time_tokens[1]+time_tokens[2]
date = date.split(' ')[0]
date_time = date+"-"+time_str
print(date_time)
'''
#interval = "2m"



if __name__ == '__main__':
    interval = "5m"
    chart = Chart()
    chart.legend(visible=True)
    chart.precision(2)
    chart_local = ChartLocal(interval, chart)
    interval = int(interval[:-1])
    date = "2024-01-25"
    kline_log = "klines_log_live_2025-01-25-130303.txt"
    line_count = 1
    while True:
        with open(kline_log, "r") as f:
            lines_after_line_count = f.readlines()[line_count:]
            for line in lines_after_line_count:
                line_count += 1
                if (line == "\n"):
                    continue
                cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume']
                tokens = line.split(",")
                date = tokens[1]
                open_p = float(tokens[2])
                high = float(tokens[3])
                low = float(tokens[4])
                close = float(tokens[5])
                volume = float(tokens[6])
                quote_volume = float(tokens[7])
                ser = pd.Series(data=[date, open_p, high, low, close, volume, quote_volume], index=cols)
                chart_local.feed_series(ser)
            f.close()
        sleep(interval*60+2)