import sys
import time
import pandas as pd
import statistics
from typing import List
from practice import get_filename
from binance import future_ticker
from time import sleep


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
    global year
    #year = "2022"
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

def is_in_range(range, value):
    if (value >= range[0] and value <= range[1]):
    #if (value >= range[0]):
        return True
    return False




def hip_lop_test():
    symbol = "BTCUSDT"
    interval = "1m"
    cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume']
    interval = int(interval[:-1])

    max_tries = 5

    cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume', 'weighted_value']
    sub_df = pd.DataFrame([], columns=cols)
    data = pd.DataFrame([], columns=cols)
    df_count = 0
    sub_df_count = 0
    max_entries = 250
    global year
    symbol = "BTCUSDT"
    end = 2
    open_p = 0

    short_entries = []
    long_entries = []
    lev = 100
    total_orders = 0


    hips = []
    lops = []

    lop_range_movement = (20, 1000)
    hip_range_movement = (20, 1000)

    contract_size = 1/10000
    size = 100
    lev = 100
    maintenance_margin_percent = 0.5
    margin = 0

    hip_bars: List[pd.Series] = []
    hip_bar_count = 0
    lop_bars: List[pd.Series] = []
    lop_bar_count = 0
    short_entries = []

    entries_by_date = {}

    low = 0
    open_t, high_t, low_t, close_t = None
    #high_t = None
    #low_t = None
    #close_t = None
    #open_date = None
    #close_date = None

    open_p, high_p, low_p, close_p = 0

    # run for 2 hours
    total_seconds = 24*60*60
    last_time_sec = int(time.time()) - 125
    req_kline = 2
    wait_time = interval*60+1
    start_time_sec = int(time.time())-130
    while -(start_time_sec - last_time_sec) < total_seconds:
        tries = 0
        while tries < max_tries:
            klines_fetched: list = future_ticker(symbol)
            if (klines_fetched is None):
                tries += 1
                sleep(1)
            else:
                break

        if (klines_fetched is None):
            print("could not fetch klines within max tries limit")
            sleep(wait_time-max_tries)
            req_kline += 1
            continue
        #klines_fetched: list = future_ticker(symbol)
        new_klines = []
        for kline in klines_fetched[::-1]:
            kline_time_sec = int(kline[0]/1000)
            if (kline_time_sec-2 < last_time_sec):
                break
            new_klines.append(kline)
            req_kline -= 1
            print(req_kline, kline)
            if (req_kline == 0):
                break
        if (len(new_klines) > 0):
            for kline in new_klines[::-1]:
                timestamp_sec = int(kline[0]/1000)
                date = get_date(timestamp_sec)
                open_p = float(kline[1])
                high = float(kline[2])
                low = float(kline[3])
                close = float(kline[4])
                volume = float(kline[5])
                quote_volume = float(kline[7])
                series: pd.Series = pd.Series(data=[date, open_p, high, low, close, volume, quote_volume], index=cols)
                





                hip_lop_live.feed_series(series)
            last_time_sec = int(new_klines[-1][0]/1000)
        print(new_klines)
        if (req_kline == 0):
            sleep(wait_time)
            req_kline += 1


def hip_lop(interval, month, days):
    interval = int(interval[:-1])
    cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume', 'weighted_value']
    sub_df = pd.DataFrame([], columns=cols)
    data = pd.DataFrame([], columns=cols)
    df_count = 0
    sub_df_count = 0
    max_entries = 250
    global year
    symbol = "BTCUSDT"
    end = 2
    open_p = 0

    short_entries = []
    long_entries = []
    lev = 100
    total_orders = 0


    hips = []
    lops = []

    lop_range_movement = (20, 1000)
    hip_range_movement = (20, 1000)

    contract_size = 1/10000
    size = 100
    lev = 100
    maintenance_margin_percent = 0.5
    margin = 0

    hip_bars: List[pd.Series] = []
    hip_bar_count = 0
    lop_bars: List[pd.Series] = []
    lop_bar_count = 0
    short_entries = []

    entries_by_date = {}

    low = 0
    open_t = None
    high_t = None
    low_t = None
    close_t = None
    #high_t = None
    #low_t = None
    #close_t = None
    #open_date = None
    #close_date = None

    open_p = 0
    high_p = 0
    low_p = 0
    close_p = 0


    for day in days:
        if (day < 10):
            day = "0" + str(day)
        date = f"{year}-{month}-{day}"
        filename = get_filename(symbol, date)
        if (sys.platform == "linux"):
            filename = filename.replace("c:\\", "/mnt/c/")
            filename = filename.replace("\\", "/")
        df = pd.read_csv(filename)
        initial_long_entries = len(long_entries)
        initial_short_entries = len(short_entries)

        long_count = 0
        short_count = 0

        longs_opened = 0
        longs_closed = 0

        shortes_opened = 0
        shorts_closed = 0

        local_long_entries = []
        local_short_entries = []


        for i, series in df.iterrows():
            log = ""
            if (open_t == None):
                with open(f"./logs/{interval}m_log.txt", "a") as f:
                    log += f"{series}\r\n"
                    f.write(log)
                    log = ""

                open_t = series['date']
                open_p = series['open']
                high_p = series['high']
                low_p = series['low']
                close_p = series['close']

            sub_df.loc[sub_df_count] = series
            sub_df_count += 1
            #print(sub_df_count, date)
            if (sub_df_count == interval):
                date = series['date']
                #open_p = sub_df['open'][0]
                #open_t = sub_df.loc[0]['date'].split(' ')[1]
                close = series['close']
                close_p = close
                close_t = date
                #close_t = sub_df.loc[sub_df_count-1]['date'].split(' ')[1]
                high = sub_df['high'].max()
                idxHigh = pd.to_numeric(sub_df['high']).idxmax()
                #print(idxHigh)
                if (high > high_p):
                    high_p = high
                    high_t = date
                #high_t = sub_df.loc[idxHigh]['date'].split(' ')[1]
                low = sub_df['low'].min()
                idxLow = pd.to_numeric(sub_df['low']).idxmin()
                #print(idxLow)
                if (low < low_p):
                    low_p = low
                    low_t = date
                #low_t = sub_df.loc[idxLow]['date'].split(' ')[1]
                volume = sub_df['volume'].sum()
                quote_volume = sub_df['quote_volume'].sum()
                weighted_value = ((high+low+close)/3)*volume
                series = pd.Series(data = [date, sub_df['open'][0], high, low, close, volume, quote_volume, weighted_value], index = ["date", "open", "high", "low", "close", "volume", "quote_volume", "weighted_value"])
                #print(series)
                log += f"{series}" + "\r\n"
                #log += f"high_t={high_t}, low_t={low_t}" + "\r\n"
                #print(ser)
                if (len(data) + 1 > max_entries):
                    start = data.index[0]
                    data = data.truncate(before=start+1, after=df_count)

                df_count += 1
                data.loc[df_count] = series
                sub_df_count = 0
    

                date = series['date'].split(' ')[0]
                curr_time = series['date'].split(' ')[1]
                #print(date, curr_time)
                #if (date == open_date and get_seconds(curr_time) < open_time_sec):
                #    continue
                #count += 1
                #if (count % 1 != 0):
                #    continue
                #count = 0
        
                hip_bars.append(series)
                hip_bar_count += 1
                if (hip_bar_count % 3 == 0):
                    h0 = hip_bars[0]['high']
                    h1 = hip_bars[1]['high']
                    h2 = hip_bars[2]['high']

                    if (is_in_range(hip_range_movement, h1-h0) and is_in_range(hip_range_movement, h1-h2)):
                        hips.append((hip_bars[0], hip_bars[1], hip_bars[2]))
                        entry = hip_bars[2]['close']
                        #global_short_entries.append(entry)
                        #local_short_entries.append(entry)
                        #if not stop_short:
                        if (short_count == 1):
                            shortes_opened += 1
                            short_count -= 1
                            short_entries.append(entry)
                            local_short_entries.append((entry, curr_time))
                            total_orders += 1
                        elif (long_count == 0):
                            shortes_opened += 1
                            long_count += 1
                            short_entries.append(entry)
                            local_short_entries.append((entry, curr_time))
                            total_orders += 1

                        #short_entries.append(entry)
                        #total_orders += 1
                        #final_short_entries.append(bars[1]['close'])
                        #long_entries.append(bars[2]['close'])
                        hip_bars = hip_bars[2:]
                        hip_bar_count -= 2
                    else:
                        hip_bars = hip_bars[1:]
                        hip_bar_count -= 1

                lop_bars.append(series)
                lop_bar_count += 1
                if (lop_bar_count % 3 == 0):
                    l0 = lop_bars[0]['low']
                    l1 = lop_bars[1]['low']
                    l2 = lop_bars[2]['low']

                    if (is_in_range(lop_range_movement, l0-l1) and is_in_range(lop_range_movement, l2-l1)):
                        lops.append((lop_bars[0], lop_bars[1], lop_bars[2]))

                        entry = lop_bars[2]['close']
                        #global_long_entries.append(entry)
                        #local_long_entries.append(entry)
                        if (long_count == 1):
                            longs_opened += 1
                            long_count -= 1
                            long_entries.append(entry)
                            local_long_entries.append((entry, curr_time))
                            total_orders += 1
                        elif (short_count == 0):
                            longs_opened += 1
                            short_count += 1
                            long_entries.append(entry)
                            local_long_entries.append((entry, curr_time))
                            total_orders += 1

                        #long_entries.append(entry)
                        #total_orders += 1
                        lop_bars = lop_bars[2:]
                        lop_bar_count -= 2
                    else:
                        lop_bars = lop_bars[1:]
                        lop_bar_count -= 1
        entry_log = ""
        if (len(long_entries) > initial_long_entries or len(short_entries) > initial_short_entries):
            #print(f"long_entries={long_entries} \r\n short_entries={short_entries} \r\n open={open_p, open_t} \r\n high_p={high, high_t} \r\n low_p={low, low_t} \r\n close_p={close, close_t} \r\n shorts_opened={shortes_opened} \r\n longs_opened={longs_opened}")
            entry_log += f"long_entries=["
            for entry in long_entries:
                sub_log = f"{entry_log}{entry}, "
                if (len(sub_log) > 94):
                    entry_log += "\n"
                    log += entry_log
                    entry_log = f"{entry}, "
                else:
                    entry_log = sub_log
            entry_log = entry_log[:-2]
            entry_log += "]\n"
            log += entry_log
            entry_log = ""
            entry_log += f"short_entries=["
            for entry in short_entries:
                sub_log = f"{entry_log}{entry}, "
                if (len(sub_log) > 94):
                    entry_log += "\n"
                    log += entry_log
                    entry_log = f"{entry}, "
                else:
                    entry_log = sub_log
            entry_log = entry_log[:-2]
            entry_log += "]\n"
            log += entry_log

            #log += f"long_entries={long_entries} \r\n short_entries={short_entries} \r\n open={open_p, open_t} \r\n high_p={high, high_t} \r\n low_p={low, low_t} \r\n close_p={close, close_t} \r\n shorts_opened={shortes_opened} \r\n longs_opened={longs_opened}" + "\r\n"
            a = 0
            b = 0
            if (len(long_entries) > 0):
                a = statistics.mean(long_entries)
            if (len(short_entries) > 0):
                b = statistics.mean(short_entries)
            entries_by_date[date] = (local_long_entries, local_short_entries, a, b)
            print(a, b)
            log += f"a={a}, b={b},\nopen={open_p}\nhigh={high_p}, high_t={high_t}\nlow={low_p}, low_t={low_t}\nclose={close_p}\n\n\n\n\n\n\n\n\n"

        #print(shortes_opened, longs_opened)
        with open(f"./logs/{interval}m_log.txt", "a") as f:
            f.write(log)
            f.close()
            log = ""


        for date in entries_by_date:
            entry_log = ""
            entry_log += f"{date}: "
            local_long_entries = entries_by_date[date][0]
            entry_log += "long_entries=[ "
            for entry in local_long_entries:
                sub_log = f"{entry_log}{entry}, "
                if (len(sub_log) > 94):
                    entry_log += "\n"
                    log += entry_log
                    entry_log = f"{entry}, "
                else:
                    entry_log = sub_log
            entry_log = entry_log[:-2]
            entry_log += "]\n"
            log += entry_log
            entry_log = ""
            entry_log += f"short_entries=["
            local_short_entries = entries_by_date[date][1]
            for entry in local_short_entries:
                sub_log = f"{entry_log}{entry}, "
                if (len(sub_log) > 94):
                    entry_log += "\n"
                    log += entry_log
                    entry_log = f"{entry}, "
                else:
                    entry_log = sub_log
            entry_log = entry_log[:-2]
            entry_log += "]\n"
            log += entry_log
            log += f"{a}, {b}"


        with open(f"./logs/{interval}m_log.txt", "a") as f:
            f.write(f"{log} \r\n {series}")
            f.close()
            log = ""


        print(date, entries_by_date[date])
        #log += f"{date}, {entries_by_date[date]}" + "\n"


    print(open_t, close_t)

if __name__ == '__main__':
    #interval = "1440m"
    year = "2025"
    interval = "2m"
    min_tr = 14
    month = "01"
    #months_list = ["11", "12"]
    months_list = ["01"]
    #months_list = list(months.keys())
    months_list.sort()
    #days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
    #        25, 26, 27, 28, 29, 30, 31]
    log_file = f"./logs/{interval}_log.txt"
    with open(f"./logs/{interval}_log.txt", "w") as f:
        f.close()



    for month in months_list:
        skip_beginning = 6
        #total_days = 31 # start_day included (>= 1)
        total_days = 1
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
                days.append(start)
                total_days -= 1
                continue
            break
            

            #start += 1
            #days.append(start)
        #print(days)
        hip_lop(interval, month, days)

        #arc = atr(interval, min_tr, month, days)
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
            