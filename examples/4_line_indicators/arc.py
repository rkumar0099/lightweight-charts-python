import sys
import pandas as pd
import statistics
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from typing import List
from practice import get_filename


months = {"12": (31, 1), "11": (30, 1), "10": (31, 1), "09": (30, 1), "08": (31, 1), "07": (31, 1), "06": (30, 1), "05": (31, 1), "04": (30, 1), "03": (31, 1), "02": (28, 1), "01": (31, 1)}

year = "2022"

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

def atr(symbol, interval, min_tr, month, days, month_days: dict, log_file):
    interval = int(interval[:-1])
    cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume', 'weighted_value']
    sub_df = pd.DataFrame([], columns=cols)
    sub_df_count = 0
    #min_tr = 28
    tr = []
    tr_count = 0
    atr = 0
    prev_atr = 0
    item = None
    flag = True
    arc = 0
    constant_c = 3.4
    global year
    #year = "2022"
    #month = "01"
    #days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    #days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    #days = [1]
    #days = [1, 2, 3, 4]
    #days = [1]
    #symbol = "1000PEPEUSDT"

    months = [int(item) for item in list(month_days.keys())]
    months.sort()
    final_arcs = []
    arcs = []
    prev_item: pd.Series = None
    for month in months:
        if (month < 10):
            month = "0" + str(month)
        else:
            month = str(month)
    
        days = month_days[month]
        print(month, days)

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
                    ser = pd.Series(data = [date, open_p, high, low, close], index = ["date", "open", "high", "low", "close"])
                    #print(ser)
                    #if (len(data) + 1 > max_entries):
                    #    start = data.index[0]
                    #    data = data.truncate(before=start+1, after=df_count)
                    a = ser['high'] - ser['low']

                    if (len(tr) == 0):
                        tr.append(a)
                        #tr[tr_count] = a
                    else:
                        #item = data.loc[data.index[-1]]
                        b = abs(prev_item['close'] - ser['high'])
                        c = abs(prev_item['close'] - ser['low'])
                        tr.append(get_tr(a, b, c))
                        #tr[tr_count] = get_tr(a, b, c)
                    prev_item = pd.Series(data = [date, close], index = ["date", "close"])
                    #print(tr)
                    tr_count += 1
                    if (tr_count > min_tr):
                        tr = tr[1::]
                        atr = ((min_tr - 1)*prev_atr + tr[-1])/min_tr
                        #atr = sum(tr)/min_tr
                        prev_atr = atr
                        #arc = constant_c*atr
                        arc = constant_c*atr

                    if (tr_count == min_tr):
                        atr = sum(tr)/min_tr
                        prev_atr = atr
                        arc = constant_c*atr
                    if (tr_count >= min_tr):
                        arcs.append(arc)
                        with open(log_file, "a") as f:
                            f.write(f"{tr}\r\n\r\n")
                        #if (len(arcs) > 3):
                        #    arc_sd = statistics.stdev(arcs)
                        print(ser['date'], tr_count, tr[-1], atr, arc)

                    sub_df_count = 0
            #if (len(arcs) > 0):
            #    final_arcs.append(statistics.mean(arcs))
    #final_arcs.sort()
    #print(final_arcs)
    #return statistics.median(final_arcs)
    #arcs.sort()
    #print(arcs)

    #return sum(tr)/len(tr)
    #return max(arcs)
    return arcs


def is_in_range(range, value):
    if (value >= range[0] and value <= range[1]):
    #if (value >= range[0]):
        return True
    return False



if __name__ == '__main__':
    #interval = "1440m"
    year = "2024"
    interval = "60m"
    min_tr = 7
    month = "01"
    months_list = ["12"]
    symbol = "AAVEUSDT"
    #months_list = list(months.keys())
    months_list.sort()
    #days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
    #        25, 26, 27, 28, 29, 30, 31]
    skip_beginning = 0
        #total_days = 31 # start_day included (>= 1)
    total_days = 23

    months_days = {}

    log_file = "log_tr.txt"

    with open(log_file, "w") as f:
        f.close()


    for month in months_list:
        #start = months[month][1]+skip_beginning-1
        start = months[month][1]-1
        end = months[month][0]
        #end = start+total_days
        days = []
        print(start, end)
        while start <= end:
            start += 1
            if (skip_beginning > 0):
                skip_beginning -= 1
                continue
            if (total_days > 0):
                if (start > end):
                    months_days[month] = days
                    break
                days.append(start)
                total_days -= 1
                continue
            break
        months_days[month] = days
        #hip_lop(interval, month, days)

        #print(months_days)
    print(months_days)
    arcs = atr(symbol, interval, min_tr, month, days, months_days, log_file)
    df = pd.DataFrame(arcs, columns=['arcs'])
    print(df.median(), df.std())
    df.plot()
    plt.show()
    #print(f"arc={arc}")
    #for day in days:
    #    arc = atr(interval, min_tr, month, [day])
    #    print(arc)
    #sic(interval)