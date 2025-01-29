import pandas as pd
from lightweight_charts import Chart
from typing import List
from practice import format_timeframe
from lightweight_charts.abstract import Line
from time import sleep


def calculate_sma(df, period: int = 50):
    df_sma = pd.DataFrame({
        'time': df['date'],
        f'SMA {period}': df['close'].rolling(window=period).mean()
    }).dropna()
    #print(df_sma)
    return df_sma

def calculate_vwap(df, period: int = 20):
    #cumm_weighted_value = df['weighted_value'][:period].sum
    df_vwap = pd.DataFrame({
        'time': df['date'],
        f'VWAP {period}': df['weighted_value'].rolling(window=period).sum() / df['volume'].rolling(window=period).sum()
    }).dropna()
    #print(df_sma)
    return df_vwap

    '''
    return pd.DataFrame({
        'time': df['date'],
        f'SMA {period}': df['close'].rolling(window=period).mean()
    }).dropna()
    '''

def get_vwap(filename):
    df = pd.read_csv(filename)
    df = df.loc[:, ['date', 'vwap']]
    #df = df.rename(columns={"date": "time", "vwap": "VWAP"})
    return df
    #return df.loc[:, ['date', 'vwap']]

'''
def format_timeframe(interval, symbol, year, month, days: List[int] = None):
    if (days is None or len(days) == 0):
        return None
    
    basepath = f"c:\\users\\rabindar kumar\\web\\trading\\data\\{year}\\{month}\\{symbol.upper()}"
    cols = ["date", "open", "high", "low", "close", "volume", "value", "weighted_value"]
    days.sort()
    rows = []
    for day in days:
        if (day < 10):
            day = "0" + str(day)
        filename = f"{basepath}\\{year}-{month}-{day}.csv"
        for row in format_to_timeframe(interval, filename, cols):
            rows.append(row)
    return pd.DataFrame(rows, columns=cols)
'''

if __name__ == '__main__':
    chart = Chart()
    chart.legend(visible=True)

    chart.precision(4)
    #date: str = "2024-12-11"
    #filename = f"10_{date}_algousdt.csv"
    #print(filename)
    days = [13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    #days = [30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8,
    #     7, 6, 5, 4, 3, 2, 1]
    symbol = "BTCUSDT"
    year = "2024"
    years_months_days = {
        2024: {12: (15, 14)}
        #2024: {12: (15, 1), 11: (30, 1), 10: (31, 1), 9: (30, 1), 8: (31, 1), 7: (31, 1), 6: (30, 1), 5: (31, 1), 4: (30, 1)}
        #2024: {12: (13, 1), 11: (30, 1), 10: (31, 1), 9: (30, 1), 8: (31, 1), 7: (31, 1), 
        #       6: (30, 1), 5: (31, 1), 4: (30, 1), 3: (31, 1), 2: (28, 1), 1: (31, 1)},
        #2023: {12: (13, 1), 11: (30, 1), 10: (31, 1), 9: (30, 1), 8: (31, 1), 7: (31, 1), 
        #       6: (30, 1), 5: (31, 1), 4: (30, 1), 3: (31, 1), 2: (28, 1), 1: (31, 1)},
        #2022: {12: (13, 1), 11: (30, 1), 10: (31, 1), 9: (30, 1), 8: (31, 1), 7: (31, 1), 
        #       6: (30, 1), 5: (31, 1), 4: (30, 1), 3: (31, 1), 2: (28, 1), 1: (31, 1)},
    }

    #month_days = {12: (13, 1), 11: (30, 1), 10: (31, 1), 9: (30, 1), 8: (31, 1), 7: (31, 1), 6: (30, 1), 5: (31, 1), 4: (30, 1), 3: (31, 1), 2: (28, 1), 1: (31, 1)}
    #month = "11"
    interval = "1m"
    df = format_timeframe(interval, symbol, years_months_days)
    print(df)
    #df = format_timeframe("240m", "BTCUSDT", "2024", "12", [13, 12, 11, 10, 9, 8, 7, 6])
    #df = pd.read_csv(filename)
    chart.set(df)
    colors = {"red": "rgba(200, 8, 8, 0.8)", "orange": "rgba(233, 159, 109, 0.8)", "blue": "rgba(2, 0, 245, 0.8)", "yellow": "rgba(248, 229, 2, 0.33)"}

    interval_avgs = {"1m": {20: "red", 50: "orange", 100: "blue"}, "10m": {20: "red", 50: "orange", 100: "blue"}, "30m": {7: "red", 17: "orange", 33: "blue", 65: "yellow"}}
    avgs = interval_avgs[interval]
    chart_lines: List[Line] = []
    for period in avgs:
        color = avgs[period]
        chart_line = chart.create_line(name=f"SMA {period}", color=color)
        chart_lines.append(chart_line)
        line_data = calculate_sma(df, period=period)
        chart_line.set(line_data)

    #line_sma100 = chart.create_line(name='SMA 100', color="rgba(2, 0, 245, 0.8)")
    #line_sma50 = chart.create_line(name='SMA 50', color="rgba(233, 159, 109, 0.8)") #
    #line_sma20 = chart.create_line(name='SMA 20', color="rgba(200, 8, 8, 0.8)")
    #line_sma10 = chart.create_line(name='SMA 10')
    line_vwap = chart.create_line(name='VWAP 50', color="rgba(76, 246, 170, 0.8)")
    chart_lines.append(line_vwap)
    vwap_data = calculate_vwap(df, period=50)
    #print(vwap_data)
    line_vwap.set(vwap_data)
    chart.show()
    #sma10_data = calculate_sma(df, period=10)
    #sma20_data = calculate_sma(df, period=20)
    #sma50_data = calculate_sma(df, period=50)
    #sma100_data = calculate_sma(df, period=100)
    #print(sma10_data)
    #sma_data_50 = calculate_sma(df, period=50)
    #sma_data_10 = calculate_sma(df, period=10)
    #line_sma10.set(sma10_data)
    #line_sma20.set(sma20_data)
    #line_sma50.set(sma50_data)
    #line_sma100.set(sma100_data)

    #chart.show(block=True)

    df2 = pd.read_csv("btc_usdt.csv")
    for i, series in df2.iterrows():
        print(series)
        chart.update(series)
        #for line in chart_lines:
        #    line.update(series)
        
        sleep(0.01)
    
    chart.show(block=True)

