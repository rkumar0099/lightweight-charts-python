import sys
import pandas as pd
import statistics
from typing import List
from practice import get_filename


def get_tr(a, b, c):
    if (a >= b and a >= c):
        return a
    if (b >= a and b >= c):
        return b
    return c

def analyse_entries(df):
    print(df)

def is_hip(bars: List[pd.Series]):
    key = "high"
    if (len(bars) != 3):
        return False
    if bars[1][key] > bars[0][key] and bars[1][key] > bars[2][key]:
        return True
    return False

def is_lop(bars):
    key = "low"
    if (len(bars) != 3):
        return False
    if bars[1][key] < bars[0][key] and bars[1][key] < bars[2][key]:
        return True
    return False

def sic(interval):
    interval = int(interval[:-1])
    cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume', 'weighted_value']
    sub_df = pd.DataFrame([], columns=cols)
    data = pd.DataFrame([], columns=cols)
    df_count = 0
    sub_df_count = 0
    max_entries = 250
    min_tr = 28
    tr = []
    tr_count = 0
    atr = 0
    prev_atr = 0
    arc = 0
    constant_c = 3
    year = "2024"
    month = "12"
    #days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    #days = [1, 2, 3, 4]
    days = [1, 2]
    symbol = "BTCUSDT"
    last_3_bar = []
    bar_count = 0
    hips = []
    hip_count = 0
    lops = []
    lop_count = 0
    flag = False
    wins = 0
    loss = 0
    trade_history = []
    open_trade = None
    open_price = 0
    for day in days:
        if (day < 10):
            day = "0" + str(day)
        date = f"{year}-{month}-{day}"
        filename = get_filename(symbol, date)
        if (sys.platform == "linux"):
            filename = filename.replace("c:\\", "/mnt/c/")
            filename = filename.replace("\\", "/")
        df = pd.read_csv(filename)

        for i, series in df.iterrows():
            if (open_price == 0):
                open_price = series['open']
            sub_df.loc[sub_df_count] = series
            sub_df_count += 1
            #if (flag):
            #    print(series)
            #    flag = False
            '''
            if (open_trade is not None):
                flag = False
                if ser['open'] <= open_trade['target']:
                    open_trade['status'] = 'win'
                    wins += 1
                    flag = True
                elif ser['open'] >=  open_trade['stop']:
                    open_trade['status'] = 'loss'
                    loss += 1
                    flag = True
                if (flag):
                    trade_history.append(open_trade)
                    open_trade = None
            '''


            #print(sub_df_count, date)
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
                #print(ser)
                if (len(data) + 1 > max_entries):
                    start = data.index[0]
                    data = data.truncate(before=start+1, after=df_count)
                a = ser['high'] - ser['close']
                if (tr_count == 0):
                    tr.append(a)
                    tr[tr_count] = a
                else:
                    item = data.loc[data.index[-1]]
                    b = abs(item['close'] - ser['high'])
                    c = abs(item['close'] - ser['low'])
                    tr.append(get_tr(a, b, c))
                    #tr[tr_count] = get_tr(a, b, c)
                #print(tr)
                tr_count += 1
                if (tr_count > min_tr):
                    tr = tr[1::]
                    atr = ((min_tr - 1)*prev_atr + tr[-1])/min_tr
                    arc = constant_c*atr
                #if (tr_count > 14):
                #    tr = tr[-1::]
                if (tr_count == min_tr):
                    atr = sum(tr)/min_tr
                    prev_atr = atr
                    arc = constant_c*atr
                #if (tr_count >= min_tr):
                    #print(ser['date'], tr_count, tr[-1], atr, arc)
                df_count += 1
                data.loc[df_count] = ser
                sub_df_count = 0
                last_3_bar.append(ser)
                bar_count += 1
                if (bar_count > 3):
                    last_3_bar = last_3_bar[1:]

                flag = is_hip(last_3_bar)
                if (flag):
                    hip_count += 1
                    e = data.index[-1]
                    hips.append((e-2, e))
                    if (open_trade is None):
                        trade = {"date": ser['date'], "entry": ser['close'], "target": ser['close']-200, "stop": ser['close']+200}
                        open_trade = trade
                    print(flag, data.loc[e-2:e], df_count)
                
                flag = is_lop(last_3_bar)
                if (flag):
                    lop_count += 1
                    e = data.index[-1]
                    lops.append((e-2, e))
                    #print(flag, data.loc[e-2:e], df_count)
                
                #flag = is_lop(last_3_bar)
                #if (flag):
                #    e = data.index[-1]
                #    print(flag, "lop", data.loc[e-2:e])
                #print(is_lop(last_3_bar))
                #if (df_count % 3 == 0):
                #    e = data.index[-1]
                    #s = data.index[df_count-14]
                    #e = data.index[-1]
                #    print(e-3, e)
                #    analyse_entries(data.loc[e-3:e])
    #print(hips, hip_count)
    #print(lops, lop_count)
    #print(trade_history, wins, loss)

def str_len():
    value = "long_entries=[60903.5, 61051.3, 61132.4, 61032.8, 61205.5, 61497.0, 61643.4, 61762.7, 61530.1,"
    print(len(value))

str_len()

def atr(interval, min_tr, month, days):
    interval = int(interval[:-1])
    cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume', 'weighted_value']
    sub_df = pd.DataFrame([], columns=cols)
    data = pd.DataFrame([], columns=cols)
    df_count = 0
    sub_df_count = 0
    max_entries = 250
    #min_tr = 28
    tr = []
    tr_count = 0
    atr = 0
    prev_atr = 0
    arc = 0
    constant_c = 3
    year = "2022"
    #month = "01"
    #days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    #days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    #days = [1]
    #days = [1, 2, 3, 4]
    #days = [1]
    symbol = "BTCUSDT"
    arcs = []
    for day in days:
        if (day < 10):
            day = "0" + str(day)
        date = f"{year}-{month}-{day}"
        filename = get_filename(symbol, date)
        if (sys.platform == "linux"):
            filename = filename.replace("c:\\", "/mnt/c/")
            filename = filename.replace("\\", "/")
        df = pd.read_csv(filename)

        for i, series in df.iterrows():
            sub_df.loc[sub_df_count] = series
            sub_df_count += 1
            #print(sub_df_count, date)
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
                #print(ser)
                if (len(data) + 1 > max_entries):
                    start = data.index[0]
                    data = data.truncate(before=start+1, after=df_count)
                a = ser['high'] - ser['close']
                if (tr_count == 0):
                    tr.append(a)
                    tr[tr_count] = a
                else:
                    item = data.loc[data.index[-1]]
                    b = abs(item['close'] - ser['high'])
                    c = abs(item['close'] - ser['low'])
                    tr.append(get_tr(a, b, c))
                    #tr[tr_count] = get_tr(a, b, c)
                #print(tr)
                tr_count += 1
                if (tr_count > min_tr):
                    tr = tr[1::]
                    atr = ((min_tr - 1)*prev_atr + tr[-1])/min_tr
                    arc = constant_c*atr
                #if (tr_count > 14):
                #    tr = tr[-1::]
                if (tr_count == min_tr):
                    atr = sum(tr)/min_tr
                    prev_atr = atr
                    arc = constant_c*atr
                if (tr_count >= min_tr):
                    arcs.append(arc)
                    #if (len(arcs) > 3):
                    #    arc_sd = statistics.stdev(arcs)
                    print(ser['date'], tr_count, tr[-1], atr, arc)
                df_count += 1
                data.loc[df_count] = ser
                sub_df_count = 0

    return arc

def get_tr(prev_kline: pd.Series, new_kline: pd.Series):
    a = new_kline['high'] - new_kline['close']
    b = abs(prev_kline['close'] - new_kline['high'])
    c = abs(prev_kline['close'] - new_kline['low'])
    if (a >= b and a >= c):
        return a
    if (b >= a and b >= c):
        return b
    return c

def get_dm(sign, prev_kline: pd.Series, new_kline: pd.Series):
    if (sign == "+"):
        if (new_kline['high'] > prev_kline['high']):
            return new_kline['high'] - prev_kline['high']
        return 0
    
    if (sign == "-"):
        if (new_kline['low'] < prev_kline['low']):
            return abs(new_kline['low']-prev_kline['low'])
        return 0

    return 0

def dx(interval, min_entries, month, days):
    interval = int(interval[:-1])
    cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume']
    sub_df = pd.DataFrame([], columns=cols)
    sub_df_count = 0
    tr = []
  
    year = "2024"
    prev_kline = None

    #month = "01"
    #days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    #days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    #days = [1]
    #days = [1, 2, 3, 4]
    #days = [1]
    symbol = "BTCUSDT"
    dm_plus = 0
    dm_minus = 0
    tr = 0
    dm_plus_14 = 0
    dm_minus_14 = 0
    tr_14 = 0

    entries_count = 0
    dx = 0

    for day in days:
        if (day < 10):
            day = "0" + str(day)
        date = f"{year}-{month}-{day}"
        print(date)
        filename = get_filename(symbol, date)
        if (sys.platform == "linux"):
            filename = filename.replace("c:\\", "/mnt/c/")
            filename = filename.replace("\\", "/")
        df = pd.read_csv(filename)

        for i, series in df.iterrows():
            sub_df.loc[sub_df_count] = series
            sub_df_count += 1
            #print(sub_df_count, date)
            if (sub_df_count == interval):
                date = series['date']
                open_p = sub_df['open'][0]
                high = sub_df['high'].max()
                low = sub_df['low'].min()
                close = series['close']
                volume = sub_df['volume'].sum()
                quote_volume = sub_df['quote_volume'].sum()
                ser = pd.Series(data = [date, open_p, high, low, close, volume, quote_volume], index = cols)
                #print(ser)
                if prev_kline is None:
                    prev_kline = ser
                    sub_df_count = 0
                    continue
                
                new_kline = ser
                sub_df_count = 0
                
                if (entries_count < 14):
                    tr_14 += get_tr(prev_kline, new_kline)
                    dm_plus_14 += get_dm("+", prev_kline, new_kline)
                    dm_minus_14 += get_dm("-", prev_kline, new_kline)
                    entries_count += 1
                    prev_kline = new_kline
                    continue
                
                dm_plus_14 = dm_plus_14 - (dm_plus_14/14) + get_dm("+", prev_kline, new_kline)
                dm_minus_14 = dm_minus_14 - (dm_minus_14/14) + get_dm("-", prev_kline, new_kline)
                tr_14 = tr_14 - (tr_14/14) + get_tr(prev_kline, new_kline)
                print(dm_plus_14, dm_minus_14, tr_14)
                di_plus = int((dm_plus_14/tr_14)*100)
                di_minus = int((dm_minus_14/tr_14)*100)
                dx = int((abs(di_plus-di_minus)/(di_plus+di_minus))*100)
                print(di_plus, di_minus, dx)
                entries_count += 1
                prev_kline = new_kline



if __name__ == '__main__':
    interval = "240m"
    min_tr = 28
    month = "01"
    #months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    months = ["12"]
    days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
            25, 26, 27]
    for month in months:
        #days = [22, 23, 24]
        #dx(interval, 14, month, days)
        pass
    #for day in days:
    #    arc = atr(interval, min_tr, month, [day])
    #    print(arc)
    #sic(interval)

    '''
    count = 0
    true_range = {}
    atr = {}
    yesterday = None
    filename = "sample_data.csv"
    #filename = "btc_usdt.csv"
    df = pd.read_csv(filename)
    for i, series in df.iterrows():
        a = float(series['high'] - series['low'])
        value = 0
        if (yesterday is None):
            value = a
            #true_range[0] = a
            yesterday = series
        else:
            b = float(abs(yesterday['close'] - series['high']))
            c = float(abs(yesterday['close'] - series['low']))
            if (a >= b and a >= c):
                value = a
                #true_range[count] = a
            elif (b >= a and b >= c):
                value = b
                #true_range[count] = b
            else:
                value = c
                #true_range[count] = c
        count += 1
        true_range[count] = value
        yesterday = series
        if (count == 7):
            atr[count] = sum(true_range.values())/7
        
        if (count > 7):
            prev_atr = atr[count - 1]
            atr[count] = (prev_atr*6 + true_range[count])/7

    
    print(true_range, "\n\n", atr)
    '''
            

def median():
    values = [70064.6, 69913.0, 69980.0, 69640.0, 69424.9, 69411.8, 69637.1, 69458.1, 69514.7, 
69356.7, 69293.0, 69399.0, 69522.3, 69908.4, 70207.2, 70467.8, 70360.7, 70212.0, 70667.7, 
71354.9, 71443.8, 71488.6, 70935.0, 71005.1, 70556.3, 70050.0, 69660.8, 69700.0, 69350.1, 
69436.5, 69074.9, 69161.7, 69283.3, 69259.1, 69366.4, 69623.4, 69506.0, 69439.7, 69464.5, 
69623.2, 69368.1, 69280.0, 69084.7, 69240.0, 69332.9, 69250.0, 69254.7]

    print(statistics.median(values), statistics.mean(values))

#median()