import pandas as pd
import requests
import time
import hashlib
import hmac
import json
import math
import statistics
from datetime import datetime
from typing import List
from binance import future_ticker
from time import sleep

from matplotlib import pyplot

from test_3 import hip_lop_test, run_mp_days


api_key=''
secret=''

year = "2024"

tested_tms = {
    "2024": [300, 100],
    "2023": [300, 100]
}

month = "04"
months = {"12": (26, 1), "11": (30, 1), "10": (31, 1), "09": (30, 1), "08": (31, 1), "07": (31, 1), "06": (30, 1), "05": (31, 1), "04": (30, 1), "03": (31, 1), "02": (28, 1), "01": (31, 1)}
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
        return r
    print(res)
    return res['id']

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
        return r
    return res['id']


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


def update_klines(filepath):
    if (filepath is None):
        return
    
    df = pd.read_csv(filepath, index_col=0)
    df_count = len(df)
    last_kline = df.loc[df.index[-1]]
    date = last_kline['date'].split(' ')[0]
    last_time = last_kline['date'].split(' ')[1]
    
    klines_fetched = future_ticker(symbol, limit=1440)
    print(get_date(int(klines_fetched[-1][0]/1000)))
    cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume']
    for kline in klines_fetched:
        timestamp_sec = int(kline[0]/1000)
        kline_date = get_date(timestamp_sec).split(' ')[0]
        kline_time = get_date(timestamp_sec).split(' ')[1]
        if (kline_date != date):
            continue
        
        if (get_seconds(kline_time) < get_seconds(last_time)):
            continue

        open_p = float(kline[1])
        high = float(kline[2])
        low = float(kline[3])
        close = float(kline[4])
        volume = float(kline[5])
        quote_volume = float(kline[7])
        series: pd.Series = pd.Series(data=[get_date(timestamp_sec), open_p, high, low, close, volume, quote_volume], index=cols)
        df.loc[df_count] = series
        df_count += 1
    print(df)
    df.to_csv(filepath)
    #print(last_kline)

def get_filepath(year, month, day):
    symbol = "BTCUSDT"
    basepath = "/mnt/c/users/rabindar kumar/web/trading/data"
    if (day < 10):
        day = "0" + str(day)
    date = f"{year}-{month}-{day}"
    filepath = f"{basepath}/{year}/{month}/{symbol}/{date}.csv"
    return filepath


def plot_pnl():
    filepath = "pnl.csv"
    df = pd.read_csv(filepath, index_col=1)
    #df.set_index('date')
    df.plot()
    pyplot.show()

def plot_md():
    filepath = "md.csv"
    df = pd.read_csv(filepath, index_col=1)
    #df.set_index('date')
    df.plot()
    pyplot.show()

def plot_mp(df):
    #filepath = "mp_log_live.csv"
    #df = pd.read_csv(filepath, index_col=0)
    #df.set_index('date')
    df.plot()
    pyplot.show()

def analyse_mp(log_file):
    if (log_file is not None):
        df = pd.read_csv(log_file)
        cols = ['date', 'mp']
        sub_df = pd.DataFrame([], columns=cols)
        interval = 10
        values = []
        count = 0
        sub_df_count = 0
        for i, series in df.iterrows():
            values.append(series['a'])
            count += 1
            if (count % interval == 0):
                sub_df.loc[sub_df_count] = pd.Series([series['date'], statistics.mean(values)], index=cols)
                sub_df_count += 1
                values = []
        sub_df.set_index('date')
        sub_df.plot()
        pyplot.show()

        return

    days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    days.reverse()
    mp_log_files = []
    for day in days:
        log_file = f"mp_log_{day}.txt"
        with open(log_file, "w") as f:
            f.close()
        mp_log_files.append(log_file)
    
    run_mp_days(days)
    

    #mp_log_files = ['mp_log_1.txt', 'mp_log_2.txt', 'mp_log_3.txt', 'mp_log_4.txt', 
    #                'mp_log_5.txt', 'mp_log_6.txt', 'mp_log_7.txt', 'mp_log_8.txt', 
    #                'mp_log_9.txt', 'mp_log_10.txt', 'mp_log_11.txt', 'mp_log_12.txt']
    fig, axes = pyplot.subplots(nrows=2, ncols=6)
    col_count = 0
    row_count = 0
    for filepath in mp_log_files:
    #filepath = "mp_log.txt"
        df = pd.read_csv(filepath)
        cols = ['date', 'mp']
        sub_df = pd.DataFrame([], columns=cols)
        interval = 10
        values = []
        count = 0
        sub_df_count = 0
        for i, series in df.iterrows():
            values.append(series['a'])
            count += 1
            if (count % interval == 0):
                sub_df.loc[sub_df_count] = pd.Series([series['date'], statistics.mean(values)], index=cols)
                sub_df_count += 1
                values = []
        sub_df.set_index('date')
        '''
        for i, series in sub_df.iterrows():
            print(i, series)
        '''
        sub_df.plot(ax=axes[row_count, col_count])
        col_count += 1
        if (col_count % 6 == 0):
            row_count += 1
            col_count = 0
        #print(sub_df.to_string())
        #plot_mp(sub_df)
    pyplot.show()

#plot_pnl()
#plot_md()
#plot_mp()

start = 1
end = 30

#days = [1,2,3,4,5,6,7,8,9,10,11,12]
#hip_lop_test(year="2024", month=12, days=days, mp_log_file="mp_log.txt")
#analyse_mp("mp_log.txt")
analyse_mp(None)

'''
def analyse_all():
    start = 0
    mid = 2
    end = 30
    #while start <= end-3:
    hip_lop_test(year="2024", month=4, days=[start+1, start+2, start+3], mp_log_file="mp_log_3.txt")
    #analyse_mp()
    start += 1
    mid += 1
'''

#analyse_mp()
#analyse_all()

#hip_lop_exec()
#hip_lop(None, None, None, 500, "sample_data_3.csv")

#hip_lop_live(None, None)
#hip_lop(None, None, None, 500, "sample_data.csv")
#hip_lop("10", None, None, 500, "2024-12-20", "14:00:00", "2024-12-21", "11:59:59", None)

#hip_lop("12", 1, None, 500)

#hip_lop(None, None, None, 500)

#sort_klines()

'''
year = "2024"
months_list = list(months.keys())
months_list.sort()
#months_list = ["01"]
for month in months_list:
    start = months[month][1]
    end = months[month][0]
    print(f"{year}-{month}")
    while start <= end:
        day = start
        if (day < 10):
            day = "0" + str(day)
        date = f"{year}-{month}-{day}"
        get_day_name(date)
        start += 1
'''

#get_day_name("2024-01-02")

#open_order(1, 94983.1)
#take_profit_order(-1, 95022.1)

#update_klines("sample_data_3.csv")


#tester = Tester("sample_data_3.csv")
#tester.test()

'''
month_list = list(months.keys())
#month_list.sort()
month_list = ["12"]
balance = 500
basepath = "/mnt/c/users/rabindar kumar/web/trading/data"
tester = Tester()
for month in month_list:
    start = months[month][1]
    end = months[month][0]
    days = []
    while start <= end:
        days.append(start)
        tester.test(get_filepath(year, month, start))
        start += 1
''' 

#filepath = get_filepath(year, "12", 15)
#tester = Tester()
#tester.test(filepath)

#hip_lop_exec()