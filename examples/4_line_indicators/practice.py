import pandas as pd
from datetime import datetime

basepath = "c:\\users\\rabindar kumar\\web\\trading\\data"

#'60m': 120, '120m': 240, 30: 60
max_days = {"1m": 3, "2m": 15, "5m": 15, "10m": 20, "15m": 30, "30m": 280, "60m": 400, "120m": 800, 
            "240m": 800, "360m": 800, "480m": 800}

supported_intervals = ["1m", "2m", "5m", "10m", "15m", "30m", "60m", "120m", "240m", "360m", "480m", "720m", "1440m"]

def format_timeframe(interval, symbol, years_months_days: dict):
    if interval not in supported_intervals:
        return None
    
    dates = []
    years = list(years_months_days.keys())
    years.sort()
    for year in years:
        months_days: dict = years_months_days[year]
        months = list(months_days.keys())
        months.sort()
        for month in months:
            day = months_days[month][1]
            end = months_days[month][0]
            while day <= end:
                if month < 10:
                    month = "0" + str(month)
                if day < 10:
                    day = "0" + str(day)
                dates.append(f"{year}-{month}-{day}")
                if (len(dates) > max_days[interval]):
                    print(f"Number of dates exceed max limit {max_days[interval]} for interval {interval}")
                    return None
                month = int(month)
                day = int(day) + 1


    interval = int(interval[:-1])
    rows = []
    cols = ["date", "open", "high", "low", "close", "volume", "quote_volume"]
    sub_rows = []
    data = None
    #days.sort()
    start = 0
    end = 0
    for date in dates:
        #print(day, start, end)
        #if (day < 10):
        #    day = "0" + str(day)
        #date = f"{year}-{month}-{day}"
        month = date.split("-")[1]
        filename = f"{basepath}\\{year}\\{month}\\{symbol.upper()}\\{date}.csv"
        print(filename)
        if (data is not None):
            #print(f"data is: {data}")
            count = end
            while count <= data.index.stop:
                sub_rows.append([data['date'][count], data['open'][count], data['high'][count], data['low'][count], data['close'][count], data['volume'][count]])
                count += 1

        df = pd.read_csv(filename)
        if (len(sub_rows) > 0):
            data = df
            count = 0
            while count <= data.index.stop:
                sub_rows.append([data['date'][count], data['open'][count], data['high'][count], data['low'][count], data['close'][count], data['volume'][count]])
                count += 1
            df = pd.DataFrame(sub_rows, columns = cols)
        sub_rows = []
        start = 0
        end = 0
        while True:
            if (end+interval > len(df)):
                print(f"df len: {len(df)}, interval is: {end+interval}")
                if (end < len(df)):
                    data = df.loc[end:]
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
            quote_volume = data['value'].sum()
            weighted_value = ((high+low+close)/3)*volume
            rows.append([date, open_p, high, low, close, volume, quote_volume, weighted_value])
            start += interval
            data = None
    cols.append('weighted_value')
    return pd.DataFrame(rows, columns=cols)



def get_row(df, index, cols):
    volume = 0
    value = 0
    high = 0
    low = 0
    close = 0
    precision = "{:.4f}"
    rangeIndex = df.index
    start = rangeIndex.start
    stop = rangeIndex.stop
    if (index >= stop or index < start):
        return None
    #if (index >= len(df) or index < 0):
    #    return None
    row = []
    for col in cols:
        if (col != "weighted_value") and col not in df:
            return None
        if col == 'volume':
            volume = df['volume'].sum()
            row.append(volume)
            continue
        if col == 'value':
            value = df['value'].sum()
            row.append(value)
            continue
        if col == 'weighted_value' and (volume > 0 and value > 0):
            weighted_value = round(((high+low+close)/3)*volume, 1)
            #vwap = precision.format(value/volume)
            row.append(weighted_value)
            continue
        if col == "high":
            high = df['high'].max()
            row.append(high)
            continue
        if col == "low":
            low = df['low'].min()
            row.append(low)
            continue
        if col == "close":
            close = df['close'][stop-1]
            row.append(close)
            continue
            #row.append(df['close'][stop-1])
        if col == "open":
            row.append(df['open'][start])
            continue

        row.append(df[col][index])

    return row

def get_filename(symbol, date):
    year = date.split("-")[0]
    month = date.split("-")[1]
    return f"{basepath}\\{year}\\{month}\\{symbol}\\{date}.csv"
    #return f"{basepath}\\{date}\\{symbol}.csv"

def format_to_timeframe(interval, filename, cols=[]):
    if interval not in supported_intervals or len(cols) == 0:
        return
    interval = int(interval[:-1])
    rows = []
    cols = ["date", "open", "high", "low", "close", "volume", "value", "weighted_value"]
    #print(filename, interval)
    df = pd.read_csv(filename)
    count = 0
    total = len(df['date'])
    index = interval - 1
    while total - count >= interval:
        data = df.loc[count:count+interval-1]
        #print(len(data))
        rows.append(get_row(data, index, cols))
        #close = data['close'][interval-1]
        #print(data)
        count += interval
        index += interval
    #print(rows)
    return rows
    #df = pd.DataFrame(rows, columns=cols)
    #df.to_csv(f"{interval}_{date}_{symbol.lower()}.csv")

def analyse_frame(df):
    sub_df = df.loc[:, ['date', 'vwap']]
    print(sub_df)

def timestamp_to_date(timestamp):
    return datetime.fromtimestamp(timestamp)

def format_file(symbol, date):
    cur_date = date
    rows = []
    cols = ["date", "open", "high", "low", "close", "volume", "value"]
    #print(date, file)
    filename = get_filename(symbol, date)
    print(filename)
    df = pd.read_csv(filename)
    dfs = []
    df_count = 0
    count = 0
    df = df.rename(columns={"open_time": "timestamp"})
    for value in df['timestamp']:
        #print(value)
        value = int(value/1000)
        dt_obj = datetime.fromtimestamp(value)
        dt_obj_str = dt_obj.date().__str__()
        '''
        if (cur_date != dt_obj_str):
            dfs.append(pd.DataFrame(rows, columns=cols))
            #analyse_frame(dfs[df_count])
            dfs[df_count].to_csv(f"{date}_algousdt.csv")
            rows = []
            cur_date = dt_obj_str
            df_count += 1
        '''
        row = [dt_obj.__str__(), df['open'][count], df['high'][count], df['low'][count], df['close'][count], df['volume'][count], df['quote_volume'][count]]
        #print(row)
        count += 1
        rows.append(row)
        #print(dt_obj.date().__str__())
        #'''
    #print(len(rows), len(cols))
    dfs.append(pd.DataFrame(rows, columns=cols))
    #analyse_frame(dfs[df_count])
    dfs[df_count].to_csv(filename)
    return dfs
    #return pd.DataFrame(rows, cols)
        #print(datetime.fromtimestamp(value))

symbol = "BTCUSDT"
year = "2024"
month = "12"
#days = ["13", "12", "11", "10", "09", "08", "07", "06"]
#days = ["05", "04", "03", "02", "01"]
#days = ["30", "29", "28", "27", "26", "25", "24", "23", "22", "21", "20", "19", "18", "17", "16", 
#        "15", "14", "13", "12", "11", "10", "09", "08", "07", "06", "05", "04", "03", "02", "01"]

#for day in days:
#    date = f"{year}-{month}-{day}"
#    format_file(symbol, date)
#days = [13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
#df = format_timeframe("60m", symbol, year, month, days)
#print(df)


#date = "2024-12-09"
#symbol = "ALGOUSDT"

#format_file(symbol, date)
#format_to_timeframe("10m", symbol, date)
#filename = "10_2024-11-24_algousdt.csv"
#df = pd.read_csv(filename)
#analyse_frame(df)



#timestamp_value = 1549836078
#timestamp_value =  1732419016

#print(f"{timestamp_to_date(timestamp_value)}")