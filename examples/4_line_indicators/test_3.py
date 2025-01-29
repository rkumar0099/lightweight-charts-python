import sys
import pandas as pd
import requests
import time
import hashlib
import hmac
import json
import math
import statistics
from lightweight_charts import Chart
from lightweight_charts.abstract import Line
from datetime import datetime
from typing import List, Dict
from binance import future_ticker
from time import sleep

api_key=''
secret=''

year = "2024"

tested_tms = {
    "2024": [300, 100],
    "2023": [300, 100]
}

month = "04"
months = {"12": (27, 1), "11": (30, 1), "10": (31, 1), "09": (30, 1), "08": (31, 1), "07": (31, 1), "06": (30, 1), "05": (31, 1), "04": (30, 1), "03": (31, 1), "02": (28, 1), "01": (31, 1)}
#days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 
        25, 26, 27, 28, 29, 30]
#day = 14
#days = [2]

symbol = "BTCUSDT"

def is_in_range(range, value):
    if (value >= range[0] and value <= range[1]):
    #if (value >= range[0]):
        return True
    return False

def gen_sign(method, url, query_string=None, payload_string=None):
    #key = ''        # api_key
    #secret = ''     # api_secret

    t = time.time()
    m = hashlib.sha512()
    m.update((payload_string or "").encode('utf-8'))
    hashed_payload = m.hexdigest()
    s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
    sign = hmac.new(secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
    return {'KEY': api_key, 'Timestamp': str(t), 'SIGN': sign}

def cancel_orders():
    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    url = '/futures/usdt/price_orders'
    query_param = ''
    # for `gen_sign` implementation, refer to section `Authentication` above
    sign_headers = gen_sign('DELETE', prefix + url, query_param)
    headers.update(sign_headers)
    r = requests.request('DELETE', host + prefix + url, headers=headers)
    print(r.json())


def open_order(size, entry):
    # coding: utf-8

    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    url = '/futures/usdt/orders'
    query_param = ''
    body = json.dumps({
        "contract":"BTC_USDT",
        "size": size,
        "iceberg": 0,
        "price": entry,
        "tif":"gtc",
        "text":"t-my-custom-id",
        "stp_act":"-",
    })
    # for `gen_sign` implementation, refer to section `Authentication` above
    sign_headers = gen_sign('POST', prefix + url, query_param, body)
    headers.update(sign_headers)
    try:
        r = requests.request('POST', host + prefix + url, headers=headers, data=body)
        res = r.json()
    except Exception as exc:
        print(exc)
        print(r)
    print(res)
    if ("id" in res):
        return res['id']
    return None

def take_profit_order(size, price):
    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    url = '/futures/usdt/price_orders'
    query_param = ''
    # price triggered order
    if (size < 0):
        rule = 2
        order_type = "close-short-order"
    else:
        rule = 1
        order_type = "close-long-order"

    body = json.dumps({
        "initial": {
            "contract":"BTC_USDT",
            "size": -size,
            "price": str(price),
            "reduce_only": True,
        },
        "trigger": {
            "strategy_type": 0,
            "rule": rule,
            "price_type": 0,
            "price": str(price),
            "expiration": 86400,
        },
        #"order_type": order_type
    })
    print(body)
    # for `gen_sign` implementation, refer to section `Authentication` above
    sign_headers = gen_sign('POST', prefix + url, query_param, body)
    headers.update(sign_headers)
    try:
        r = requests.request('POST', host + prefix + url, headers=headers, data=body)
        res = r.json()
        print(res)
    except Exception as exc:
        print(exc)
        print(r)
    print(res)
    if ("id" in res):
        return res['id']
    return None


def get_date(timestamp):
    #return datetime.fromtimestamp(timestamp/1000).isoformat(sep=' ', timespec='milliseconds')
    return datetime.fromtimestamp(int(timestamp/1000)).__str__()

def get_datetime(timestamp):
    #date = get_date(time.time()*1000)
    date = get_date(timestamp)
    time_tokens = date.split(' ')[1].split(":")
    time_str = time_tokens[0]+time_tokens[1]+time_tokens[2]
    date = date.split(' ')[0]
    date_time = date+"-"+time_str
    return date_time

def sort_klines():
    files = ["sample_data.csv", "sample_data_2.csv"]
    cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume']
    rows = []
    for file in files:
        df = pd.read_csv(file)
        for i, series in df.iterrows():
            date = series['date']
            open_p = series['open']
            high = series['high']
            low = series['low']
            close = series['close']
            volume = series['volume']
            quote_volume = series['quote_volume']
            #ser = pd.Series(data=[date, open_p, high, low, close, volume, quote_volume], index=cols)
            rows.append([date, open_p, high, low, close, volume, quote_volume])
    df = pd.DataFrame(rows, columns=cols)
    
    print(df)
    df.to_csv("sample_data_3.csv")
    


class Live:

    def __init__(self, log_file):
        self.cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume']
        self.df_count = 0
        self.df: pd.DataFrame = pd.DataFrame([], columns=self.cols)
        self.kline_log_file = log_file
        index = ","
        for col in self.cols:
            index += col + ","
        index = index[:-1]
        self.write_kline_log(index)
        #self.hip_lop = Hip_Lop()
        self.orders_opened = 0
    
    def write_kline_log(self, log):
        with open(self.kline_log_file, "a") as f:
            f.write(log + "\n")
            f.close()
    
    def feed_series(self, series: pd.Series):
        print(series)
        log = f"{self.df_count},{series['date']},{series['open']},{series['high']},{series['low']},{series['close']},{series['volume']},{series['quote_volume']}"
        self.write_kline_log(log)
        self.df_count += 1
        #self.df.loc[self.df_count] = series
        #self.df_count += 1

        #new_orders = self.hip_lop.run_series(series)
        '''
        for order in new_orders:
            print(order)
            try:
                size = order[0]
                price = str(order[1])
                tp = str(order[2])
                if (open_order(size, price) is not None and take_profit_order(size, tp) is not None):
                    self.orders_opened += 1
            except Exception as exc:
                print(exc)
        print(self.orders_opened)
        '''
    def print_df(self):
        filename = f"{symbol}_{get_date(int(time.time()))}.csv"
        self.df.to_csv(filename)

def get_filepath(symbol, year, month, day):
    basepath = "/mnt/c/users/rabindar kumar/web/trading/data"
    if (sys.platform != "linux"):
        basepath = basepath.replace("/mnt/c", "c:").replace("/", "\\")


    #"C:\\Users\\Rabindar Kumar\\web\\trading\\data\\2024\12\BTCUSDT"


    if (month < 10):
        month  = "0" + str(month)

    if (day < 10):
        day = "0" + str(day)

    date = f"{year}-{month}-{day}"
    filepath = f"{basepath}/{year}/{month}/{symbol}/{date}.csv"
    if (sys.platform != "linux"):
        filepath.replace("/", "\\")
    return filepath


class MP:
    def __init__(self, log_file):
        self.log_file = log_file
        with open(self.log_file, "w") as f:
            f.write("date,a,b\n")
            f.close()
        self.hips = []
        self.lops = []
        self.lop_range_movement = (5, 1000)
        self.hip_range_movement = (5, 1000)


        self.hip_bars: List[pd.Series] = []
        self.hip_bar_count = 0
        self.lop_bars: List[pd.Series] = []
        self.lop_bar_count = 0

        self.long_entries = []
        self.short_entries = []

        self.a = 0
        self.b = 0


    def feed_series(self, series):
        hips = []
        lops = []

        lop_range_movement = (5, 1000)
        hip_range_movement = (5, 1000)


        hip_bars: List[pd.Series] = self.hip_bars
        hip_bar_count = self.hip_bar_count
        lop_bars: List[pd.Series] = self.lop_bars
        lop_bar_count = self.lop_bar_count
   
        long_entries = self.long_entries
        short_entries = self.short_entries

        a = self.a
        b = self.b


        initial_long_entries = len(long_entries)
        initial_short_entries = len(short_entries)


        hip_bars.append(series)
        hip_bar_count += 1
        if (hip_bar_count % 3 == 0):
            h0 = hip_bars[0]['high']
            h1 = hip_bars[1]['high']
            h2 = hip_bars[2]['high']

            if (is_in_range(hip_range_movement, h1-h0) and is_in_range(hip_range_movement, h1-h2)):
                hips.append((hip_bars[0], hip_bars[1], hip_bars[2]))
                entry = hip_bars[2]['close']
                short_entries.append(entry)

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
                #short_entries.append(bars[1]['close'])
                #final_short_entries.append(bars[1]['close'])
                #if not stop_long:
                entry = lop_bars[2]['close']
                long_entries.append(entry)
                lop_bars = lop_bars[2:]
                lop_bar_count -= 2
            else:
                lop_bars = lop_bars[1:]
                lop_bar_count -= 1
        flag0 = False
        flag1 = False
        if (len(long_entries) > initial_long_entries):
            flag0 = True
        if (len(short_entries) > initial_short_entries):
            flag1 = True

        if (flag0):
            a = statistics.mean(long_entries)
        if (flag1):
            b = statistics.mean(short_entries)
        if ((a > 0 and b > 0) and (flag0 == True or flag1 == True)):
            print(a, b, flag0, flag1)
            with open(self.log_file, "a") as f:
                f.write(f"{series['date']}, {a}, {b}\n")
                f.close()


        self.hips = hips
        self.lops = lops


        self.hip_bars = hip_bars
        self.hip_bar_count = hip_bar_count
        self.lop_bars = lop_bars
        self.lop_bar_count = lop_bar_count
   
        self.long_entries = long_entries
        self.short_entries = short_entries

        self.a = a
        self.b = b

class ChartLocal:
    def __init__(self, interval, chart: Chart):
        self.interval = interval
        self.interval = int(interval[:-1])
        self.chart_init = False
        self.cols = ["date", "open", "high", "low", "close", "volume", "quote_volume"]
        self.data = pd.DataFrame([], columns=self.cols)
        self.df_count = 0
        self.sub_df_cols =  ["date", "open", "high", "low", "close", "volume", "quote_volume"]
        self.sub_df = pd.DataFrame([], columns=self.sub_df_cols)
        self.sub_df_count = 0
        self.chart = chart
        self.chart.legend(visible=True)
        self.chart.precision(2)

    def feed_interval(self, series):
        try:
            if not self.chart_init:
                #ser = pd.Series(data=[series['date'], series['open'], series['high'], series['low'], series['close'], series['volume'], series['quote_volume'] ], index=self.cols)
                print(f"setting chart data, chart init={self.chart_init}")
                self.data.loc[self.df_count] = series
                self.chart.set(self.data)
                self.chart.show()
                self.chart_init = True
            else:
                print("updating chart")
                self.chart.update(series)
                
        except Exception as exc:
            print(exc)

    def feed_series(self, series):
        self.sub_df.loc[self.sub_df_count] = series
        self.sub_df_count += 1
        if (self.sub_df_count == self.interval):
            date = series['date']
            open_p = self.sub_df['open'][0]
            high = self.sub_df['high'].max()
            low = self.sub_df['low'].min()
            close = series['close']
            volume = self.sub_df['volume'].sum()
            quote_volume = self.sub_df['quote_volume'].sum()
            ser = pd.Series([date, open_p, high, low, close, volume, quote_volume], index=self.cols)
            try:
                if not self.chart_init:
                    #ser = pd.Series(data=[series['date'], series['open'], series['high'], series['low'], series['close'], series['volume'], series['quote_volume'] ], index=self.cols)
                    print(f"setting chart data, chart init={self.chart_init}")
                    self.data.loc[self.df_count] = ser
                    self.chart.set(self.data)
                    self.chart.show()
                    self.chart_init = True
                else:
                    print("updating chart")
                    self.chart.update(ser)
                self.sub_df_count = 0
            except Exception as exc:
                print(f"exception while setting chart data")
                print(exc)
        

class MP_Days:

    def __init__(self, log_file):
        self.mp_prev: Dict[int, MP] = {}


    def run_days(self, year, month, days):
        mp_prev: Dict[int, MP] = {}

        for day in days:
            log_file = f"mp_log_{day}.txt"
            mp = MP(log_file)
            mp_prev[day] = mp
            filepath = get_filepath(year, month, day)
            df = pd.read_csv(filepath)
            for i, series in df.iterrows():
                for i in mp_prev:
                    mp = mp_prev[i]
                    mp.feed_series(series)
        self.mp_prev = mp_prev

def run_mp_days(days):
    mp_days = MP_Days(None)
    mp_days.run_days(year="2022", month=1, days=days)
    for i in mp_days.mp_prev:
        mp = mp_days.mp_prev[i]
        print(len(mp.long_entries))

class Hip_Lop_Test:

    def __init__(self, interval, log_file):
        self.log_file = log_file
        with open(self.log_file, "w") as f:
            f.close()
        self.interval = int(interval[:-1])
        cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume', 'weighted_value']
        self.cols = cols
        self.sub_df = pd.DataFrame([], columns=cols)
        self.data = pd.DataFrame([], columns=cols)
        self.df_count = 0
        self.sub_df_count = 0
        self.max_entries = 250

        self.symbol = "BTCUSDT"
        end = 2
        open_p = 0

        self.short_entries = []
        self.long_entries = []
        self.lev = 100
        self.total_orders = 0


        self.hips = []
        self.lops = []

        self.lop_range_movement = (20, 1000)
        self.hip_range_movement = (25, 1000)

        self.contract_size = 1/10000
        self.size = 100
        self.lev = 100
        self.maintenance_margin_percent = 0.5
        self.margin = 0

        self.hip_bars: List[pd.Series] = []
        self.hip_bar_count = 0
        self.lop_bars: List[pd.Series] = []
        self.lop_bar_count = 0

        self.entries_by_date = {}

        self.low = 0
        self.open_t = None
        self.high_t = None
        self.low_t = None
        self.close_t = None
        

        self.open_p = 0
        self.high_p = 0
        self.low_p = 0
        self.close_p = 0

        self.long_count = 0
        self.short_count = 0

        self.longs_opened = 0
        self.longs_closed = 0

        self.shorts_opened = 0
        self.shorts_closed = 0

        self.log = ""

        self.short_entries_time = []
        self.long_entries_time = []

        self.local_long_entries = []
        self.local_short_entries = []

        self.sbt = 0
        self.lbt = 0

        self.short_ahead = 0
        self.long_ahead = 0

        self.prev_long_entry = None
        self.prev_short_entry = None

        self.global_short_entries = []
        self.global_long_entries = []
    

    def feed_series(self, series: pd.Series):
        interval = self.interval
        cols = self.cols
        sub_df = self.sub_df
        data =  self.data
        df_count = self.df_count
        sub_df_count = self.sub_df_count
        max_entries = self.max_entries
        symbol = self.symbol


        short_entries = self.short_entries
        long_entries = self.long_entries
        total_orders = self.total_orders


        hips = self.hips
        lops = self.lops

        lop_range_movement = self.lop_range_movement
        hip_range_movement = self.hip_range_movement

        contract_size = self.contract_size
        size = self.size
        lev = self.lev
        maintenance_margin_percent = self.maintenance_margin_percent
        margin = self.margin

        hip_bars: List[pd.Series] = self.hip_bars
        hip_bar_count = self.hip_bar_count
        lop_bars: List[pd.Series] = self.lop_bars
        lop_bar_count = self.lop_bar_count

        entries_by_date = {}

        low = 0
        open_t = self.open_t
        high_t = self.high_t
        low_t = self.low_t
        close_t = self.close_t
        #high_t = None
        #low_t = None
        #close_t = None
        #open_date = None
        #close_date = None

        open_p = 0
        high_p = 0
        low_p = 0
        close_p = 0

        date = series['date']


        initial_long_entries = len(self.long_entries)
        initial_short_entries = len(self.short_entries)

        long_count = self.long_count
        short_count = self.short_count

        longs_opened = self.longs_opened
        longs_closed = self.longs_closed

        shorts_opened = self.shorts_opened
        shorts_closed = self.shorts_closed

        local_long_entries = self.local_long_entries
        local_short_entries = self.local_short_entries       


        log = ""
        if (open_t == None):
            with open(self.log_file, "a") as f:
                log += f"{series}\r\n"
                f.write(log)
                log = ""
            open_t = series['date']
            high_t = series['date']
            low_t = series['date']
            close_t = series['date']
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
            #log += f"{series}" + "\r\n"
            #log += f"high_t={high_t}, low_t={low_t}" + "\r\n"
            #print(ser)
            if (len(data) + 1 > max_entries):
                start = data.index[0]
                data = data.truncate(before=start+1, after=df_count)

            df_count += 1
            data.loc[df_count] = series
            sub_df_count = 0
            

            date = series['date']
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
                    #local_short_entries.append(entry)
                    #if not stop_short:
                    #self.global_short_entries.append(entry)
                    #short_entries.append(entry)
                    #local_short_entries.append((entry, curr_time))
                    
                    if (short_count == 1):
                        #self.lbt += time.time() - self.lot
                        shorts_opened += 1
                        short_count -= 1
                        short_entries.append(entry)
                        local_short_entries.append((entry, curr_time))
                        total_orders += 1
                    elif (long_count == 0):
                        self.sot = time.time()
                        shorts_opened += 1
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
                    #self.global_long_entries.append(entry)
                    #long_entries.append(entry)
                    #local_long_entries.append((entry, curr_time))
                    #local_long_entries.append(entry)
                    if (long_count == 1):
                        #self.sbt += time.time() - self.sot
                        print(self.sbt)
                        #sbt += time.time() - sot
                        longs_opened += 1
                        long_count -= 1
                        long_entries.append(entry)
                        local_long_entries.append((entry, curr_time))
                        total_orders += 1
                    elif (short_count == 0):
                        self.lot = time.time()
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
            
            #print(series['date'], len(self.global_short_entries), len(self.global_long_entries))

            if (shorts_opened > longs_opened and self.short_ahead == 0):
                self.short_ahead = time.time()
            
            if (shorts_opened < longs_opened and self.long_ahead == 0):
                self.long_ahead = time.time()
            
            elif(shorts_opened == longs_opened):
                if (self.short_ahead > 0):
                    self.sbt += time.time() - self.short_ahead
                else:
                    self.lbt += time.time() - self.long_ahead
                
                self.short_ahead = 0
                self.long_ahead = 0

        entry_log = ""
        if (len(long_entries) > initial_long_entries or len(short_entries) > initial_short_entries):
            #print(f"long_entries={long_entries} \r\n short_entries={short_entries} \r\n open={open_p, open_t} \r\n high_p={high, high_t} \r\n low_p={low, low_t} \r\n close_p={close, close_t} \r\n shorts_opened={shorts_opened} \r\n longs_opened={longs_opened}")
            entry_log += f"long_entries=["
            for entry in long_entries:
                sub_log = f"{entry_log}{entry}, "
                if (len(sub_log) > 94):
                    entry_log += "\n"
                    log += entry_log
                    entry_log = f"{entry}, "
                else:
                    entry_log = sub_log
            if (entry_log[-1] != '['):
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
            if (entry_log[-1] != '['):
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
            #entries_by_date[date] = (local_long_entries, local_short_entries, a, b)
            #print(a, b)
            log += f"a={a}, b={b}, sbt={self.sbt}, lbt={self.lbt}\n\n\n\n"

            #print(shorts_opened, longs_opened)
            with open(self.log_file, "a") as f:
                f.write(log)
                f.close()
                log = ""


            entry_log = ""
            entry_log += f"{date}: "
            #local_long_entries = entries_by_date[date][0]
            entry_log += "long_entries=["
            for entry in local_long_entries:
                sub_log = f"{entry_log}{entry}, "
                if (len(sub_log) > 94):
                    entry_log += "\n"
                    log += entry_log
                    entry_log = f"{entry}, "
                else:
                    entry_log = sub_log
            if (entry_log[-1] != '['):
                entry_log = entry_log[:-2]
            entry_log += "]\n"
            log += entry_log
            entry_log = ""
            entry_log += f"short_entries=["
            #local_short_entries = entries_by_date[date][1]
            for entry in local_short_entries:
                sub_log = f"{entry_log}{entry}, "
                if (len(sub_log) > 94):
                    entry_log += "\n"
                    log += entry_log
                    entry_log = f"{entry}, "
                else:
                    entry_log = sub_log
            if (entry_log[-1] != '['):
                entry_log = entry_log[:-2]
            entry_log += "]\n"
            log += entry_log
            log += f"{a}, {b}\n\n\n\n\n"


            with open(self.log_file, "a") as f:
                f.write(log)
                f.close()
                log = ""

        
        self.sub_df = sub_df
        self.data = data
        self.df_count = df_count
        self.sub_df_count = sub_df_count


        self.short_entries = short_entries
        self.long_entries = long_entries
        self.total_orders = total_orders


        self.hips = hips
        self.lops = lops


        self.hip_bars = hip_bars
        self.hip_bar_count = hip_bar_count
        self.lop_bars = lop_bars
        self.lop_bar_count = lop_bar_count


        low = 0
        self.open_t = open_t
        self.high_t = high_t
        self.low_t = low_t
        self.close_t = close_t
        #high_t = None
        #low_t = None
        #close_t = None
        #open_date = None
        #close_date = None

        open_p = 0
        high_p = 0
        low_p = 0
        close_p = 0


        initial_long_entries = len(self.long_entries)
        initial_short_entries = len(self.short_entries)

        self.long_count = long_count
        self.short_count = short_count

        self.longs_opened = longs_opened
        self.longs_closed = longs_closed

        self.shorts_opened = shorts_opened
        self.shorts_closed = shorts_closed

        self.local_long_entries = local_long_entries
        self.local_short_entries = local_short_entries 



def fetch_klines():
    symbol = "BTCUSDT"
    interval = "1m"
    klines_fetched = future_ticker(symbol)
    new_klines = []
    rows = []
    cols=['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume']
    for kline in klines_fetched[::-1]:
        new_klines.append(kline)

    for kline in new_klines[::-1]:
        date = get_date(kline[0])
        open_p = float(kline[1])
        high = float(kline[2])
        low = float(kline[3])
        close = float(kline[4])
        volume = float(kline[5])
        quote_volume = float(kline[7])
        rows.append([date, open_p, high, low, close, volume, quote_volume])

    pd.DataFrame(rows, columns=cols).to_csv("latest.csv")

def hip_lop_test(year, month, days, mp_log_file):
    interval = "2m"
    interval = int(interval[:-1])
    #filepath = get_filepath(year, month, day)
    #df = pd.read_csv(filepath)
    cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume']
    sub_df = pd.DataFrame([], columns=cols)
    sub_df_count = 0
    hlt = Hip_Lop_Test(f"{interval}m", f"./logs/{interval}m_log_test3.txt")
    mp = MP(mp_log_file)
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
        filepath = get_filepath(year, month, day)
        df = pd.read_csv(filepath)

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
                    series = pd.Series(data = [date, sub_df['open'][0], high, low, close, volume, quote_volume], index=cols)
                    #print(series)
                    hlt.feed_series(series)
                    mp.feed_series(series)
                    sub_df_count = 0

        print(hlt.sbt, hlt.lbt)


def hip_lop_live(month, day, flag, chart):
    symbol = "BTCUSDT"
    interval = "1m"
    #interval = int(interval[:-1])
    cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume']
    interval = int(interval[:-1])

    max_tries = 5
    #if (flag):
        #date = get_date(int(time.time()))
    timestamp = time.time()*1000
    date_time = get_datetime(timestamp)
    #chart_local = ChartLocal("10m", chart)
    hll = Live(f"klines_log_live_{date_time}.txt")
    mp = MP(f"mp_log_live_{date_time}.txt")
    hlt = Hip_Lop_Test("2m", f"./logs/2m_log_live_{date_time}.txt")
    #else:
    #    hip_lop_live = Live("Kline_log.txt")
    #    mp = MP(f"mp_log.txt")
    #    hlt = Hip_Lop_Test("2m", f"./logs/2m_log.txt")
        #hip_lop_test()
    # run for 2 hours
    sub_df = pd.DataFrame([], columns=cols)
    sub_df_count = 0

    total_seconds = 2*24*60*60
    last_time_sec = int(time.time())-125
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
            req_kline += 1
            sleep(wait_time-max_tries)
            continue

        #klines_fetched: list = future_ticker(symbol)
        new_klines = []
        for kline in klines_fetched[::-1]:
            #print(kline)
            kline_time_sec = kline[0]/1000
            if (kline_time_sec-2 < last_time_sec):
                break

            '''
            ser = pd.Series(data = [get_date(kline[0]), float(kline[1]), float(kline[2]), float(kline[3]), float(kline[4]), float(kline[5]), float(kline[7])], index=cols)
            hlt.feed_series(ser)
            mp.feed_series(ser)
            chart_local.feed_series(ser)
            hll.feed_series(ser)
            sub_df.loc[sub_df_count] = series
            sub_df_count += 1
            if (sub_df_count == interval):
                open_p = sub_df['open']
                high = sub_df['high'].max()
                low = sub_df['low'].min()
                close = sub_df['close']
                volume = sub_df['volume'].sum()
                quote_volume = sub_df['quote_volume'].sum()
                date = get_date(time.time())
                ser = pd.Series(data = [date, open_p, high, low, close, volume, quote_volume], index=cols)

                sub_df_count = 0
            '''
            new_klines.append(kline)
            req_kline -= 1
            print(req_kline, kline)

            if (req_kline == 0):
                break
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

                hll.feed_series(series)
                mp.feed_series(series)
                hlt.feed_series(series)
                #chart_local.feed_series(series)

            last_time_sec = int(new_klines[-1][0]/1000)

            #print(new_klines)
        if (req_kline == 0):
            sleep(wait_time)
            req_kline += 1

    '''
    print(kline)
    timestamp = kline[0]
    last_time_sec = int(timestamp/1000)
    print(timestamp)
    print(get_date(last_time_sec))
    print(kline)
    '''

    #hip_lop.print_df()


def get_seconds(open_time):
    tokens = open_time.split(":")
    return int(tokens[0])*60*60 + int(tokens[1])*60 + int(tokens[2])

years = ["2022", "2023", "2024"]

year_start_day = {
    "2022": "Sat",
    "2023": "Sun",
    "2024": "Mon",
}
week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def next_day(current_day):
    if current_day not in week_days:
        return None
    index = week_days.index(current_day)+1
    if (index == 7):
        return week_days[0]
    return week_days[index]

def get_day_name(date: str):
    tokens = date.split("-")
    year = tokens[0]
    month = int(tokens[1])
    day = int(tokens[2])
    start_day = year_start_day[year]
    count = day-1
    month -= 1
    while month > 0:
        if (month < 10):
            key = "0" + str(month)
        else:
            key = str(month)
        count += months[key][0]
        month -= 1
    
    skip_c = int(count / 7)
    count -= skip_c*7
    day = week_days[count]
    #print(date, day)
    return week_days[count]

def get_str(day):
    if (day < 10):
        day = "0" + str(day)
    return day



#mean()
#fetch_klines()

'''
hlt: Hip_Lop_Test = Hip_Lop_Test("2m")
df = pd.read_csv("latest.csv")
for i, series in df.iterrows():
    hlt.feed_series(series)
'''

#year = "2022"
#hip_lop_live(None, None, False)


#days = [7, 8, 9]
#hip_lop_test(year, month=1, days=days)

if __name__ == '__main__':
    chart = Chart()
    chart.legend(visible=True)
    chart.precision(2)
    '''
    cols = ['date', 'open', 'high','low', 'close', 'volume', 'quote_volume']
    klines_fetched = future_ticker("BTCUSDT", limit=1000)
    data = pd.DataFrame([], columns = cols)
    chart_init = False
    chart_local = ChartLocal("2m", chart)
    for kline in klines_fetched[::]:
        print(get_date(kline[0]))
        series = pd.Series(data=[get_date(kline[0]), kline[1], kline[2], kline[3], kline[4], kline[5], kline[7]], index=cols)
        chart_local.feed_series(series)
        
        if not (chart_init):
            data.loc[0] = series
            chart.set(data)
            chart.show()
            chart_init = True
            continue
        chart.update(series)
        #chart.show(block=True)
        
    chart.show(block=True)
    '''


    hip_lop_live(None, None, True, chart)