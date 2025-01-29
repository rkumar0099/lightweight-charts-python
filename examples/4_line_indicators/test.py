import pandas as pd
from time import sleep
from lightweight_charts import Chart
from lightweight_charts.abstract import Line
from typing import List, Dict

def reverse_df():
    filename = "btc_usdt.csv"
    out_file = "btc_usdt_3.csv"
    df = pd.read_csv(filename)
    print(df.index)
    start = df.index.stop - 1
    end = 0
    cols = ["date", "open", "high", "low", "close", "volume", "quote_volume"]
    rows = []
    while start >= end:
        data = df.loc[start]
        row = []
        for col in cols:
            row.append(data[col])
        rows.append(row)
        start -= 1
    pd.DataFrame(rows, columns=cols).to_csv(out_file)

    #start = df.index.start
    #end = 
    #print(start, end)


def read_data():
    filename = "btc_usdt.csv"
    df = pd.read_csv(filename)
    #df = df.reindex(index=df.index[::-1])
    # reverse the frame, binance tickers fetch from latest to old, chart takes df from old to latest
    df = df.iloc[::-1]
    print(df)
    return df

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
    #"60m": {20: "short", 50: "intermmediate", 100: "long"}
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
mas = [7, 20, 50]

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

if __name__ == '__main__':
#def format_timeframe():
    #interval = "10m"
    #interval = "1440m"
    #interval = "2880m"
    #no_of_files = int(int(interval[:-1])/1440)
    #print(no_of_files)
    interval = "10m"
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

    klines_1m = []
    chart = Chart()
    chart.legend(visible=True)
    chart.precision(6)
    year = "2022"
    month = 1
    symbol = "AAVEUSDT"
    #start_date = "2024-12-15"
    start_day = 1
    #start_date = "2024-11-28"
    #end_date = "2024-12-12"
    #if (month < 10):
    #    month = "0" + str(month)
    #start_date = f"{year}-{month}-{start_day}"
    #mid_date = "2024-12-14"
    #end_date = "2024-12-15"
    #frames: List[pd.DataFrame] = []
    '''
    df_count = 0
    df = pd.DataFrame([], columns = cols)
    file_count = no_of_files
    while file_count > 0:
        month = int(month)
        start_day = int(start_day)
        if (start_day > days_in_month[month]):
            start_day = 1
            month += 1
            if (month > 12):
                month = 1
                year = int(year) + 1
                if (year > 2024):
                    break
                year = str(year)
        if (month < 10):
            month = "0" + str(month)
        if (start_day < 10):
            start_day = "0" + str(start_day)

        start_date = f"{year}-{month}-{start_day}"
        frame = pd.read_csv(f"{basepath}\\{year}\\{month}\\{symbol}\\{start_date}.csv")
        for i, series in frame.iterrows():
            df.loc[df_count] = series
            df_count += 1
        #frames.append(pd.read_csv(f"{basepath}\\{year}\\{month}\\{symbol}\\{start_date}.csv"))
        #df = pd.concat() pd.read_csv(f"{basepath}\\{year}\\{month}\\{symbol}\\{start_date}.csv")
        start_day += 1
        file_count -= 1
    #print(frames)
    print(df)
    '''
    df_count = 0
    data = pd.DataFrame([], columns = cols)
    sub_df = pd.DataFrame([], columns=cols)
    sub_df_count = 0
    start = 0
    lines = {}
    #max_entries = 250
    # set chart data and add lines
    #(data, sub_df, lines)  = init_chart(interval=interval, df=df, max_entries=max_entries, chart=chart)
    #start = data.index[0]
    #df_count = data.index[-1]
    #sub_df_count = len(sub_df)
    #chart.show()
    interval = int(interval[:-1])
    #days = ["11", "12", "13", "14", "15"]
    #days = [17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    #days = [14]
    #days = ["14", "15", "16", "17"]
    #days = ["14", "15"]
    #days = 620 # (start day excluded)
    days = 320
    day = start_day
    month = int(month)
    is_chart_init = False
    #days = []
    #days.sort()
    ser_data = {}
    ser_data = {"high": 0, "low": 0, "volume": 0, "quote_volume": 0}
    while days > 0:
        if (day > days_in_month[month]):
            day = 1
            month += 1
            if (month > 12):
                #continue
                year = int(year) + 1
                if (year > 2024):
                    break
                year = str(year)
                month = 1
        if (month < 10):
            month = "0" + str(month)
        if (day < 10):
            day = "0" + str(day)
        date = f"{year}-{month}-{day}"
        print(date)
        try:
            df = pd.read_csv(f"{basepath}\\{year}\\{month}\\{symbol}\\{date}.csv")
        except Exception as exc:
            print(exc)
            break
        day = int(day)
        month = int(month)
        day += 1
        days -= 1
        #sub_df_count = len(sub_df)
        start_index = 0
        end_index = len(df)-1
        while start_index < end_index:
            s = start_index
            e = start_index
            if (start_index+interval > end_index):
                e = end_index
            else:
                e = start_index+interval
            sub_df = df.loc[s:e]
            start_index += interval
            sub_df_count += interval
            #start_index += (e-s+1)
            #sub_df_count += (e-s+1)
        #for i, series in df.iterrows():
        #    sub_df.loc[sub_df_count] = series
        #    sub_df_count += 1
            #print(sub_df_count, date)
            date = sub_df.loc[e]['date']
            #date = series['date']
            open_p = sub_df.loc[s]['open']
            #open_p = sub_df['open'][0]
            #close = series['close']
            close = sub_df.loc[e]['close']
            high = sub_df['high'].max()
            low = sub_df['low'].min()
            volume = sub_df['volume'].sum()
            quote_volume = sub_df['quote_volume'].sum()
            if ("open" not in ser_data):
                ser_data['open'] = open_p
                ser_data['low'] = open_p
                #print(ser_data)
            else:
                open_p = ser_data['open']
            ser_data['high'] = max(ser_data['high'], high)
            high = ser_data['high']
            ser_data['low'] = min(ser_data['low'], low)
            low = ser_data['low']
            ser_data['volume'] = ser_data['volume'] + volume
            volume = ser_data['volume']
            ser_data['quote_volume'] = ser_data['quote_volume'] + quote_volume
            quote_volume = ser_data['quote_volume']
            #print(sub_df_count)
            # if (sub_df_count == interval):
            if (sub_df_count == interval):
                #date = sub_df.loc[e]['date']
                #date = series['date']
                #open_p = sub_df.loc[s]['open']
                #open_p = sub_df['open'][0]
                #open_p = ser_data['open']
                #high = ser_data['high']
                #low = ser_data['low']
                #volume = ser_data['volume']
                #quote_volume = ser_data['quote_volume']
                #close = series['close']
                #close = sub_df.loc[e]['close']
                #high = sub_df['high'].max()
                #low = sub_df['low'].min()
                #volume = sub_df['volume'].sum()
                #quote_volume = sub_df['quote_volume'].sum()
                weighted_value = ((high+low+close)/3)*volume
                ser = pd.Series(data = [date, open_p, high, low, close, volume, quote_volume, weighted_value], index = ["date", "open", "high", "low", "close", "volume", "quote_volume", "weighted_value"])
                #print(ser)
                #print(ser)
                ser_data = {}
                ser_data = {"high": 0, "low": 0, "volume": 0, "quote_volume": 0}
                if (len(data) > mas[-1]+2):
                    e = data.index[-1]
                    data = data.loc[e-3:e]
                    #data = data.truncate(before=start+1, after=df_count)
                df_count += 1
                data.loc[df_count] = ser
                if not (is_chart_init):
                    chart.set(data)
                    chart.show()
                    is_chart_init = True
                    print(f"chart init: {is_chart_init}")
                    sub_df_count = 0
                    continue
                    
                #print(data)
                    #print(len(data), data.loc[data.index[-1]])
                    #print(len(data), date)
                #print(ser)
                chart.update(ser)
                lines = update_lines(data, lines, interval)
                #print(lines)
                sub_df_count = 0
                sleep(2)
                #(data, lines) = update_chart(ser, data, chart, lines)
                #sub_df_count = 0
                #chart.update(ser)
                #ser.name = count
                #count += 1
                #data.loc[count] = ser
            else:
                print(sub_df_count)
                break


    chart.show(block=True)


    '''
    df = pd.read_csv("btc_usdt_2.csv")
    (data, sub_df) = format_df_to_interval(interval, df)
    count = len(data)
    print(data, "\n", len(sub_df), "\n", sub_df)
    chart.precision(4)
    chart.set(data)
    chart.show()
    #cols = ['']
    #colors = {"red"}
    sub_df_count = len(sub_df)
    max_entries = 250
    start = 0
    filenames = ['btc_usdt_3.csv', 'btc_usdt_4.csv']
    #filenames = ['btc_usdt_3.csv']
    for filename in filenames:
        for i, series in pd.read_csv(filename).iterrows():
            sub_df.loc[sub_df_count] = series
            sub_df_count += 1
            if (sub_df_count == interval):
                date = series['date']
                open_p = sub_df['open'][0]
                close = series['close']
                high = sub_df['high'].max()
                low = sub_df['low'].min()
                volume = sub_df['volume'].sum()
                quote_volume = sub_df['quote_volume'].sum()
                weighted_value = ((high+low+close)/3)*volume
                ser = pd.Series(data = [date, open_p, high, low, close, volume, quote_volume, weighted_value], index = ["date", "open", "high", "low", "close", "volume", "quote_volume", "weighted_value"])
                chart.update(ser)
                #ser.name = count
                count += 1
                data.loc[count] = ser
                if (count >= max_entries):
                    start += 1
                    data = data.truncate(before=start, after=count)
                    #update_smas(data, sma_lines)
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
                            lines[name].update(sma_df.loc[sma_df.index[-1]])

                        #print(data.loc[end-period:end])
                #print(data) 
                #print(ser.name)
                #data[count] = ser
                #data = data.append(ser)
                #print(ser)
                #print(data)
                sub_df_count = 0
                sleep(0.01)
    '''
    '''
    for i, series in pd.read_csv("btc_usdt_4.csv").iterrows():
        sub_df.loc[sub_df_count] = series
        sub_df_count += 1
        if (sub_df_count == interval):
            date = series['date']
            open_p = sub_df['open'][0]
            close = series['close']
            high = sub_df['high'].max()
            low = sub_df['low'].min()
            volume = sub_df['volume'].sum()
            quote_volume = sub_df['quote_volume'].sum()
            weighted_value = ((high+low+close)/3)*volume
            ser = pd.Series(data = [date, open_p, high, low, close, volume, quote_volume, weighted_value], index = ["date", "open", "high", "low", "close", "volume", "quote_volume", "weighted_value"])
            chart.update(ser)
            #ser.name = count
            data.loc[count] = ser
            #print(ser.name)
            #data[count] = ser
            #data = data.append(ser)
            #print(ser)
            #print(data)
            count += 1
            sub_df_count = 0
            sleep(0.01)
    '''

    #chart.show(block=True)
    
    #print(data, sub_df)
            

    #print(format_df_to_interval(interval, df))
    '''
    count = len(df)
    #chart.precision(4)
    #chart.set(df)
    max_entries = 250

    for i, series in df.iterrows():
        k_lines_1m.append()


    # next_df = pd.read_csv("btc_usdt_4.csv")
    # for i, series in next_df.iterrows():
    '''
    #return

#format_timeframe()

'''
if __name__ == '__main__':
    #reverse_df()
    df = pd.read_csv("btc_usdt_3.csv")
    #interval = "1m"
    interval = "5m"
    #df = read_data()
    chart = Chart()
    chart.legend(visible=True)

    chart.precision(4)
    start = 0
    #mid = 300
    #end = len(df)
    mid = 200
    end = 1020
    initial_df = df.iloc[0:mid]
    #print(len(initial_df))
    #ser = initial_df.iloc[0, :]
    #print(ser, type(ser))
    #print(initial_df)
    
    chart.set(initial_df)
    chart.show()
    sleep(1)
    avgs = {
        "short": {
            "30m": 7,
            "10m": 20,
            "5m": 40,
            "2m": 20,
            "1m": 50
        },
        "intermmediate": {
            "30m": 17,
            "10m": 50,
            "5m": 100,
            "2m": 50,
            "1m": 100
        },
        "long": {
            "30m": 33,
            "10m": 100,
            "5m": 200,
            "2m": 100,
            "1m": 195
        }
        #"30m": {"short": 7, "intermmediate": 17, "long": 33},
        #"10m": {"short": 20, "intermmediate": 50, "long"}
    }
    #colors = {20: "red", 50: "orange", 100: "blue", 200: "yellow"}
    avgs_colors = {"short": "red", "intermmediate": "orange", "long": "blue"}
    sma_lines: Dict[int, Line] = {}
    #periods = [20, 50, 100]
    periods = [20, 50, 100]
    terms = ["short", "intermmediate", "long"]
    for term in terms:
        period = avgs[term][interval]
    #for period in periods:
        color = avgs_colors[term]
        sma_lines[period] = chart.create_line(name=f'SMA {period}', color=color_codes[color])
        #sma_lines.append(chart.create_line(f'SMA {period}', color="rgba(200, 8, 8, 0.8)"))
        #sma_lines.append(chart.create_line(f'SMA 50', color="rgba(233, 159, 109, 0.8)"))

    for term in terms:
        period = avgs[term][interval]
        line_data = calculate_sma(initial_df, period=period)
        print(line_data)
        sma_lines[period].set(line_data)
        #line.set(calculate_sma(initial_df, period=))

    count = 0
    for i, series in df.iterrows():
        count += 1
        if (count <= mid):
            continue
        if (count >= end):
            break
        #print(series)
        chart.update(series)
        initial_df.loc[count] = series
        #print(initial_df)
        if (len(initial_df) > mid+5):
            start += 1
            initial_df = initial_df.truncate(before=start, after=count)
            #print(initial_df)
        #    print(len(initial_df))
        #= pd.concat([initial_df, series._])
        #initial_df = initial_df.append(series, ignore_index=True)
        #print(len(initial_df))
        
        for term in terms:
            period = avgs[term][interval]
            name = f"SMA {period}"
            data = calculate_sma(initial_df, period)
            #if (len(data) >= period):
            
            ser = data.loc[data.index[-1]]
            #print(type(ser), ser)

            #print(type(row))
            #ser = pd.Series(row)
            #print(row)
            #print(data.loc[lastIndex])
            #print(data.iloc[[lastIndex]].)
            #print(data.iloc[:-1])
            sma_lines[period].update(ser)
            #print(sma_lines[period].data, sma_lines[period]._last_bar)
        sleep(0.01)
        
    
    chart.show(block=True)

'''

'''
time      153    2024-12-16 10:32:00
Name: time, dtype: ...
SMA 20        153    104815.57
Name: SMA 20, dtype: float64
dtype: object

'''


