import pandas as pd
from time import sleep
from lightweight_charts import Chart
from lightweight_charts.abstract import Line
from typing import List, Dict
from test_3 import get_filepath, ChartLocal
from binance import future_ticker
from test_3 import get_date


def calculate_sma(df, period: int = 50):
    df_sma = pd.DataFrame({
        'time': df['date'],
        f'SMA {period}': df['close'].rolling(window=period).mean()
    }).dropna()
    #print(df_sma)
    return df_sma

color_codes = {"gray": "rgba(213, 186, 184, 0.65)", "red": "rgba(200, 8, 8, 0.8)", "light-red": "rgba(233, 104, 92, 0.65)", "orange": "rgba(233, 159, 109, 0.8)", "blue": "rgba(2, 0, 245, 0.8)", "yellow": "rgba(248, 229, 2, 0.33)"}
trends = ["mini-short", "short", "intermmediate", "long"]

trends_interval_ma = {
    "10m": {20: "short", 50: "intermmediate", 100: "long"},
    "60m": {7: "short", 20: "intermmediate", 50: "long"}
}

#trends = ["long", "long-long"]
#interval = "5m"

# 1m, long-long (300)
# 1m, long-long (400)
smas = {
    "1m": {"mini-short": 25, "short": 50, "intermmediate": 100, "long": 200, "long-long": 300},
    #"1m": {"mini-short": 25, "short": 50, "intermmediate": 100, "long": 300, "long-long": 400},
    "2m": {"mini-short": 10, "short": 20, "intermmediate": 50, "long": 100},
    "5m": {"mini-short": 10, "short": 20, "intermmediate": 50, "long": 100},
    "10m": {"mini-short": 10, "short": 20, "intermmediate": 50, "long": 100},
    #"30m": {"mini-short": 10, "short": 20, "intermmediate": 50, "long": 100},
    "15m": {"mini-short": 7, "short": 17, "intermmediate": 33, "long": 65},
    "30m": {"mini-short": 7, "short": 17, "intermmediate": 33, "long": 65},
    "60m": {"mini-short": 7, "short": 17, "intermmediate": 33, "long": 65},
    "240m": {"mini-short": 7, "short": 17, "intermmediate": 100, "long": 200},
    "480m": {"mini-short": 7, "short": 17, "intermmediate": 100, "long": 200},
    "1440m": {"mini-short": 7, "short": 20, "intermmediate": 100, "long": 200},
    "2880m": {"mini-short": 7, "short": 20, "intermmediate": 50, "long": 100}
}

colors = {"60m": {"mini-short": 7, "short": 17, "intermmediate": 33, "long": 65},
    "smas": { "mini-short": "gray", "short": "light-red", "intermmediate": "orange", "long": "blue", "long-long": "yellow" },
}

lines_data = {}
#mas = [20, 50, 100, 200]
mas = [20, 50, 100]

def init_chart(interval, df, max_entries, chart: Chart):
    interval = int(interval[:-1])
    no_of_files = int(interval/1440)
    rows = []
    cols = ["date", "open", "high", "low", "close", "volume", "quote_volume"]
    df_cols = ["date", "open", "high", "low", "close", "volume", "quote_volume", "weighted_value"]
    start = 0
    end = 0
    df_count_start = 0
    df_count = 0
    out_df = pd.DataFrame([], columns=df_cols)
    lines: Dict[str, Line] = {} # map lines to names
    #max_entries = 250
    while True:
        if (end+interval > len(df)):
            #print(f"df len: {len(df)}, interval is: {end+interval}")
            #if (end < len(df)):
            #    data = df.loc[end:]
            break
        end += interval
        data = df.loc[start:end]
        #print(data)
        date = data['date'][end-1]
        open_p = data['open'][start]
        high = data['high'].max()
        low = data['low'].min()
        close = data['close'][end-1]
        volume = data['volume'].sum()
        quote_volume = data['quote_volume'].sum()
        weighted_value = ((high+low+close)/3)*volume
        ser = pd.Series([date, open_p, high, low, close, volume, quote_volume, weighted_value], df_cols)
        out_df.loc[df_count] = ser
        if (df_count < 1):
            chart.set(out_df)
        else:
            chart.update(ser)
        df_count += 1
        #if (df_count <= 1)
        if (df_count > max_entries):
            df_count_start += 1
            out_df = out_df.truncate(before=df_count_start, after=df_count)
        #rows.append([date, open_p, high, low, close, volume, quote_volume, weighted_value])
        for trend in trends:
            key = f"{interval}m"
            period = smas[key][trend]
            if (df_count > period):
                index = out_df.index[-1]
                #print(len(out_df), df_count, index)
                sma_data = out_df.loc[index-period:index]
                sma_df = calculate_sma(sma_data, period)
                #print(sma_df)
                name = f'SMA {period}'
                if name not in lines:
                    color = colors["smas"][trend]
                    lines[name] = chart.create_line(name=name, color=color_codes[color])
                    lines[name].set(sma_df)
                else:
                    lines[name].update(sma_df.loc[sma_df.index[-1]])
        start += interval

    sub_rows = []
    #sub_df = pd.DataFrame([], columns=cols)
    #print(len(sub_df))
    #remaining_rows = []
    count = 0
    while end < len(df):
        ser = df.loc[end]
        sub_rows.append([ser['date'], ser['open'], ser['high'], ser['low'], ser['close'], ser['volume'], ser['quote_volume']])
        #print(end)
        #sub_df[count] = df.loc[end]
        #count += 1
        #remaining_rows.append(df.loc[end])
        end += 1
    sub_df = pd.DataFrame(sub_rows, columns=cols)
    #cols.append('weighted_value')
    #return (pd.DataFrame(rows, columns=cols), sub_df)
    return (out_df, sub_df, lines)

def update_lines(data: pd.DataFrame, lines: Dict[str, Line], interval):
    len_data = len(data)
    for ma in mas:
        if (ma in lines_data):
            (value, last_index) = lines_data[ma]
            new_index = data.index[-1]
            if (last_index < new_index):
                close = data.loc[new_index]['close']
                new_value = ((ma-1)*value+close)/ma
                lines_data[ma] = (new_value, new_index)
                name = f'SMA {ma}'
                ser = pd.Series(data=[data.loc[new_index]['date'], new_value], index=['time', name])
                lines[name].update(ser)
        elif (ma == len_data):
            sma_df = calculate_sma(data, ma)
            name = f'SMA {ma}'
            index = data.index[-1]
            value = sma_df.loc[sma_df.index[-1]][name]
            key = f"{interval}m"
            trend = trends_interval_ma[key][ma]
            color = colors["smas"][trend]
            lines[name] = chart.create_line(name=name, color=color_codes[color])
            lines[name].set(sma_df)
            lines_data[ma] = (value, index)

    '''
        if (ma > len_data):
            return data
        name = f"SMA {ma}"
        if (ma == len_data):
            df = calculate_sma(data, ma)
            lines[ma] = calculate_sma(data, ma)
            
        if (len(data) > ma):
            lines[ma] = 
    e = data.index[-1]
    return data.loc[e-1:e]

    for trend in trends:
        key = f"{interval}m"
        period = smas[key][trend]
        if (len(data) > period):
            end = data.index[-1]
            sma_data = data.loc[end-period:end]
            sma_df = calculate_sma(sma_data, period)
            #print(sma_df)
            name = f'SMA {period}'
            if name not in lines:
                color = colors["smas"][trend]
                lines[name] = chart.create_line(name=name, color=color_codes[color])
                lines[name].set(sma_df)
            else:
                ser = sma_df.loc[sma_df.index[-1]]
                #print(name, ser)
                lines[name].update(ser)
    '''
    return lines



def format_df_to_interval(interval, df):
    rows = []
    cols = ["date", "open", "high", "low", "close", "volume", "quote_volume"]
    start = 0
    end = 0
    while True:
        if (end+interval > len(df)):
            #print(f"df len: {len(df)}, interval is: {end+interval}")
            #if (end < len(df)):
            #    data = df.loc[end:]
            break
        end += interval
        data = df.loc[start:end]
        #print(data)
        date = data['date'][end-1]
        open_p = data['open'][start]
        high = data['high'].max()
        low = data['low'].min()
        close = data['close'][end-1]
        volume = data['volume'].sum()
        quote_volume = data['quote_volume'].sum()
        weighted_value = ((high+low+close)/3)*volume
        rows.append([date, open_p, high, low, close, volume, quote_volume, weighted_value])
        start += interval
    sub_rows = []
    #sub_df = pd.DataFrame([], columns=cols)
    #print(len(sub_df))
    #remaining_rows = []
    count = 0
    while end < len(df):
        ser = df.loc[end]
        sub_rows.append([ser['date'], ser['open'], ser['high'], ser['low'], ser['close'], ser['volume'], ser['quote_volume']])
        #print(end)
        #sub_df[count] = df.loc[end]
        #count += 1
        #remaining_rows.append(df.loc[end])
        end += 1
    sub_df = pd.DataFrame(sub_rows, columns=cols)
    cols.append('weighted_value')
    return (pd.DataFrame(rows, columns=cols), sub_df)

def get_kline_ser(series):
    cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume']
    date = series['date']
    open_p = float(series['open'])
    high = float(series['high'])
    low = float(series['low'])
    close = float(series['close'])
    volume = float(series['volume'])
    quote_volume = float(series['quote_volume'])
    return pd.Series(data=[date, open_p, high, low, close, volume, quote_volume], index=cols)

def plot_chart_latest(symbol, chart_local: ChartLocal):
    klines_fetched: list = future_ticker(symbol)
    if (klines_fetched is None):
        return
    print(klines_fetched)
    cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume']
    #klines_fetched: list = future_ticker(symbol)
    new_klines = []
    for kline in klines_fetched[::-1]:
        new_klines.append(kline)

    print(f"new klines = {len(new_klines)}")
    if (len(new_klines) > 0):
        for kline in new_klines[::-1]:
            #timestamp = time.time()
            date = get_date(kline[0])
            open_p = float(kline[1])
            high = float(kline[2])
            low = float(kline[3])
            close = float(kline[4])
            volume = float(kline[5])
            quote_volume = float(kline[7])
            series: pd.Series = pd.Series(data=[date, open_p, high, low, close, volume, quote_volume], index=cols)
            chart_local.feed_series(series)
            #chart_local.feed_interval(series)


if __name__ == '__main__':
#def format_timeframe():
    #interval = "10m"
    #interval = "1440m"
    #interval = "2880m"
    #no_of_files = int(int(interval[:-1])/1440)
    #print(no_of_files)
    interval = "60m"
    #interval = "240m"
    #interval = "480m"
    max_entries = 250
    #smas = [20]
    #lines: Dict[str, Line] = {} # map lines to names
    # whether indicator added to chart
    #indicators = {
    #    "sma": [20, 50, 100],
    #    "vwap": [50, 100, 200]
    #}
    #indicators = ["sma20", "sma50", "sma100", "vwap50"]
    #cols = ["date", "open", "high", "low", "close", "volume", "quote_volume", "weighted_value"]
    cols = ["date", "open", "high", "low", "close", "volume", "quote_volume", "weighted_value"]
    basepath = "c:\\users\\rabindar kumar\\web\\trading\\data"
    days_in_month = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    is_chart_init = False
    symbol = "BTCUSDT"
    klines_1m = []
    chart = Chart()
    chart.legend(visible=True)
    chart.precision(8)
    chart_local = ChartLocal(interval, chart)
    plot_chart_latest(symbol, chart_local)

    '''
    interval = int(interval[:-1])
    year = "2024"
    month = 12
    end = days_in_month[month]
    start = 1
    while start <= end:
        filepath = get_filepath(symbol, year, month, start)
        df = pd.read_csv(filepath)
        for i, series in df.iterrows():
            chart_local.feed_series(get_kline_ser(series))
        start += 1
    '''


    '''
    day = 7
    df_count = 0
    data = pd.DataFrame([], columns = cols)
    sub_df = pd.DataFrame([], columns=cols)
    sub_df_count = 0
    start = 0
    lines = {}
    filepath = get_filepath(year, month, day)
    df = pd.read_csv(filepath)
    for i, series in df.iterrows():
        sub_df.loc[sub_df_count] = series
        sub_df_count += 1
        #print(sub_df_count, date)
        if (sub_df_count == interval):
            date = series['date']
            close = series['close']
            #close_t = sub_df.loc[sub_df_count-1]['date'].split(' ')[1]
            high = sub_df['high'].max()
            idxHigh = pd.to_numeric(sub_df['high']).idxmax()
            #print(idxHigh)
            #high_t = sub_df.loc[idxHigh]['date'].split(' ')[1]
            low = sub_df['low'].min()
            idxLow = pd.to_numeric(sub_df['low']).idxmin()
            #print(idxLow)
            #low_t = sub_df.loc[idxLow]['date'].split(' ')[1]
            volume = sub_df['volume'].sum()
            quote_volume = sub_df['quote_volume'].sum()
            weighted_value = ((high+low+close)/3)*volume
            ser = pd.Series(data = [date, sub_df['open'][0], high, low, close, volume, quote_volume, weighted_value], index=cols)

            #print(ser)
            if (len(data) + 1 > max_entries):
                start = data.index[0]
                data = data.truncate(before=start+1, after=df_count)

            df_count += 1
            data.loc[df_count] = ser
            sub_df_count = 0

            if (not is_chart_init):
                chart.set(data)
                chart.show()
                is_chart_init = True
                print(f"chart init: {is_chart_init}")
                continue

                    
            #print(data)
                #print(len(data), data.loc[data.index[-1]])
                #print(len(data), date)
            #print(ser)
            chart.update(ser)
            lines = update_lines(data, lines, interval)
            #print(lines)
            sleep(2)
    '''

    chart.show(block=True)