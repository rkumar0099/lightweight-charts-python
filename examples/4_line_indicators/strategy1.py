import sys
import pandas as pd
import requests
import time
import hashlib
import hmac
import json
import math
import statistics
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



def get_date(timestamp_sec):
    dt_obj = datetime.fromtimestamp(timestamp_sec)
    #dt_obj_str = dt_obj.date().__str__()
    #return dt_obj_str
    return dt_obj.__str__()

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

    def __init__(self):
        self.cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume']
        self.df_count = 0
        self.df: pd.DataFrame = pd.DataFrame([], columns=self.cols)
        self.kline_log_file = f"symbol_{get_date(int(time.time()))}.txt"
        index = ","
        for col in self.cols:
            index += col + ","
        index = index[:-1]
        self.write_kline_log(index)
        #self.hip_lop = Hip_Lop()
        self.orders_opened = 0
    
    def write_kline_log(self, log):
        with open(self.kline_log_file, "a") as f:
            f.write(log + "\r\n")
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

def get_filepath(year, month, day):
    symbol = "BTCUSDT"
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

        self.open = 0
        self.high = 0
        self.low = 0
        self.close = 0

        self.date = None


    def feed_series(self, series):
        self.date = series['date']

        if (self.open == 0):
            self.open = series['open']
            self.high = series['high']
            self.low = series['low']
            self.close = series['close']
        
        if (series['high'] > self.high):
            self.high = series['high']
        
        if (series['low'] < self.low):
            self.low = series['low']
        
        self.close = series['close']

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
            #print(a, b, flag0, flag1)
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


def mp_test(year, month, day):
    filepath = get_filepath(year, month, day)
    df = pd.read_csv(filepath)
    mp = MP("mp_log.txt")
    for i, series in df.iterrows():
        mp.feed_series(series)
        if (mp.a > 0):
            if (abs(mp.a - mp.open) > 200):
                print(mp.date, mp.a, mp.open, mp.close)
                return True
    return False


months = [1]
months.reverse()
for month in months:
    start = 1
    end = 30
    if (month == 2):
        end = 28
    count = 0
    while start <= end:
        if (mp_test("2025", month, start)):
            count += 1
        start += 1
    print(month, count)


def hip_lop_test(year, month, days, mp_log_file):
    interval = "2m"
    interval = int(interval[:-1])
    #filepath = get_filepath(year, month, day)
    #df = pd.read_csv(filepath)
    cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume']
    sub_df = pd.DataFrame([], columns=cols)
    sub_df_count = 0
    #hlt = Hip_Lop_Test(f"{interval}m", f"./logs/{interval}m_log_test3.txt")
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

        #print(hlt.sbt, hlt.lbt)


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

year = "2022"
#hip_lop_live(None, None, False)


#days = [7, 8, 9]
#hip_lop_test(year, month=1, days=days)