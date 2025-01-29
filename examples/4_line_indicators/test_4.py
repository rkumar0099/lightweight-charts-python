import pandas as pd
import requests
import time
import hashlib
import hmac
import json
import math
from datetime import datetime
from typing import List
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

def hip_live():
    return

def lop(month, days):
    basepath = "/mnt/c/users/rabindar kumar/web/trading/data"
    for day in days:
        if (day < 10):
            day = "0" + str(day)
        date = f"{year}-{month}-{day}"
        filepath = f"{basepath}/{year}/{month}/{symbol}/{date}.csv"
        interval = "1m"
        interval = int(interval[:-1])

        lops = []
        total_pnl = 0
        total_hits = 0
        total_miss = 0
      
        max_drawdown = 0

        #range_movement = (10, 10000)
        range_movement = (1, 500)
        #range_movement = (30, 500)
        #range_movement = (50, 500)
        #range_movement = (1, 500)
        #range_movement = (1, 10000)
        df = pd.read_csv(filepath)
        #print(df)
        #tm = 300 # target movement
        tm = 2000
        win_tm = 500
        sm = tm/2
        #tm = 300
        sl = tm/100
        reward = win_tm/100
        rrf = 2
        pnl = 0
        hits = 0
        miss = 0
        bars: List[pd.Series] = []
        bar_count = 0
        short_entries = []
        long_entries = []

        for i, series in df.iterrows():
            close = series['close']          
            entries = long_entries.copy()
            for entry in entries:
                diff = close-entry
                if (diff < -tm):
                    long_entries.remove(entry)
                    miss += 1
                    pnl -= sl
                if (diff > win_tm):
                    long_entries.remove(entry)
                    hits += 1
                    pnl += reward
             
            '''
            entries = final_short_entries.copy()
            for entry in entries:
                remove_index = []
            #for index, entry in enumerate(short_entries):
                diff = close-entry
          final_short_entries.remove(entry)
            ''' 
            '''       
            entries = final_long_entries.copy()
            for entry in entries:
                diff = close-entry
                if (diff < -tm):
                    pnl -= sl
                    miss += 1
                    final_long_entries.remove(entry)
                    #remove_index.append(index)
                if (diff > win_tm):
                    pnl += reward
                    hits += 1
                    print(entry, close)
                    final_long_entries.remove(entry)
            '''
            
            if (pnl < max_drawdown):
                max_drawdown = pnl
            bars.append(series)
            bar_count += 1
            if (bar_count % 3 == 0):
                l0 = bars[0]['low']
                l1 = bars[1]['low']
                l2 = bars[2]['low']

                if (is_in_range(range_movement, l0-l1) and is_in_range(range_movement, l2-l1)):
                    lops.append((bars[0], bars[1], bars[2]))
                    #short_entries.append(bars[1]['close'])
                    #final_short_entries.append(bars[1]['close'])
                    long_entries.append(bars[1]['close'])
                    bars = bars[2:]
                    bar_count -= 2
                else:
                    bars = bars[1:]
                    bar_count -= 1

        #print(len(hips), hips[0])
        total_hits += hits
        total_miss += miss
        #print(short_entries, long_entries, pnl, hits, miss)
    #consecutive_short_miss_list.sort()
    #consecutive_short_hits_list.sort()
    #print(consecutive_short_miss_list, max_drawdown)
    #print(consecutive_short_miss_list.sort())
    #print(consecutive_short_hits_list, consecutive_short_miss_list)
        for entry in long_entries:
            diff = entry-close
            pnl += (diff/100)
            #print(entry, close)
        total_pnl += pnl
        fee = (hits+miss+len(long_entries))*70/100
        print(date, pnl, fee, pnl-fee, hits, miss, len(long_entries))
        return (date, pnl, fee, pnl-fee, hits, miss, len(long_entries))
    #return (total_pnl, total_hits, total_miss)

def hip(month, days):
    basepath = "/mnt/c/users/rabindar kumar/web/trading/data"
    total_orders = 0
    for day in days:
        if (day < 10):
            day = "0" + str(day)
        date = f"{year}-{month}-{day}"
        filepath = f"{basepath}/{year}/{month}/{symbol}/{date}.csv"
        interval = "1m"
        interval = int(interval[:-1])

        hips = []
        total_pnl = 0
        total_hits = 0
        total_miss = 0
        consecutive_short_hits_list = []
        consecutive_long_hits_list = []
        consecutive_short_miss_list = []
        consecutive_long_miss_list = []
        consecutive_short_hits = 0
        consecutive_short_miss = 0
        consecutive_long_hits = 0
        consecutive_long_miss = 0
        max_drawdown = 0
        rrf = 4
        short_orders = {}
        long_orders = {}
        final_short_entries = []
        final_long_entries = []

        range_movement = (20, 500)
        #range_movement = (10, 500)
        #range_movement = (30, 500)
        #range_movement = (50, 500)
        #range_movement = (1, 500)
        #range_movement = (1, 10000)
        df = pd.read_csv(filepath)
        #print(df)
        #tm = 300 # target movement
        tm = 2000
        win_tm = 500
        sm = tm/2
        #tm = 300
        sl = tm/100
        reward = win_tm/100
        rrf = 2
        pnl = 0
        hits = 0
        miss = 0
        bars: List[pd.Series] = []
        bar_count = 0
        short_entries = []
        long_entries = []
        short_sl_hit = False
        long_sl_hit = False
        short_open = False
        long_open = False
        for i, series in df.iterrows():
            close = series['close']
            date_time = series['date']
            entries = short_entries.copy()
            for entry in entries:
                remove_index = []
            #for index, entry in enumerate(short_entries):
                diff = close-entry
                if (diff > tm):
                    short_entries.remove(entry)
                    miss += 1
                    pnl -= sl
                    '''
                    if (consecutive_short_hits > 20):
                        final_long_entries.append(entry)
                    if (consecutive_short_hits > 0):
                        consecutive_short_hits_list.append((consecutive_short_hits, entry, close))
                        consecutive_short_hits = 0
                    consecutive_short_miss += 1
                    '''
                        # go long
                    #remove_index.append(index)
                if (diff < -win_tm):
                    short_entries.remove(entry)
                    hits += 1
                    pnl += reward
                    '''
                    if (consecutive_short_miss > 20):
                        final_short_entries.append(close)
                    if (consecutive_short_miss > 0):
                        consecutive_short_miss_list.append((consecutive_short_miss, entry, close))
                        consecutive_short_miss = 0
                    consecutive_short_hits += 1
                    '''
            '''
            entries = long_entries.copy()
            for entry in entries:
                diff = close-entry
                if (diff < -tm):
                    long_entries.remove(entry)
                    miss += 1
                    if (consecutive_long_hits > 20):
                        final_short_entries.append(entry)
                    if (consecutive_long_hits > 0):
                        consecutive_long_hits_list.append(consecutive_long_hits)
                        consecutive_long_hits = 0
                    consecutive_long_miss += 1
                    #remove_index.append(index)
                if (diff > win_tm):
                    long_entries.remove(entry)
                    hits += 1
                    if (consecutive_long_miss > 20):
                        final_long_entries.append(entry)
                    if (consecutive_long_miss > 0):
                        consecutive_long_miss_list.append(consecutive_long_miss)
                        consecutive_long_miss = 0
                    consecutive_long_hits += 1
            '''
            '''
            entries = final_short_entries.copy()
            for entry in entries:
                remove_index = []
            #for index, entry in enumerate(short_entries):
                diff = close-entry
                if (diff > tm):
                    miss += 1
                    pnl -= sl
                    final_short_entries.remove(entry)
                    
                        # go long
                    #remove_index.append(index)
                if (diff < -win_tm):
                    hits += 1
                    pnl += reward
                    print(entry, close)
                    final_short_entries.remove(entry)
            '''

            '''        
            entries = final_long_entries.copy()
            for entry in entries:
                diff = close-entry
                if (diff < -tm):
                    pnl -= sl
                    miss += 1
                    final_long_entries.remove(entry)
                    #remove_index.append(index)
                if (diff > win_tm):
                    pnl += reward
                    hits += 1
                    final_long_entries.remove(entry)
            '''
            if (pnl < max_drawdown):
                max_drawdown = pnl
            bars.append(series)
            bar_count += 1
            if (bar_count % 3 == 0):
                h0 = bars[0]['high']
                h1 = bars[1]['high']
                h2 = bars[2]['high']

                if (is_in_range(range_movement, h1-h0) and is_in_range(range_movement, h1-h2)):
                    hips.append((bars[0], bars[1], bars[2]))
                    entry = bars[1]['close']
                    '''
                    if (len(short_entries) > 0):
                        min_entry = min(short_entries)
                        max_entry = max(short_entries)
                        if (entry-min_entry < -500 or entry-max_entry > 500):
                            short_entries.append(entry)
                        #elif (entry-max_entry > 500):
                        #    short_entries.append(entry)
                    else:
                    '''
                    short_entries.append(entry)
                    total_orders += 1
                    #final_short_entries.append(bars[1]['close'])
                    #long_entries.append(bars[2]['close'])
                    bars = bars[2:]
                    bar_count -= 2
                else:
                    bars = bars[1:]
                    bar_count -= 1

        #print(len(hips), hips[0])
        #total_pnl += pnl
        total_hits += hits
        total_miss += miss
        #print(short_entries, long_entries, pnl, hits, miss)
    #consecutive_short_miss_list.sort()
    #consecutive_short_hits_list.sort()
    #print(consecutive_short_miss_list, max_drawdown)
    #print(consecutive_short_miss_list.sort())
    #print(consecutive_short_hits_list, consecutive_short_miss_list)
        for entry in short_entries:
            diff = entry-close
            if (diff < 0):
                hits += 1
            else:
                miss += 1
            pnl_before = pnl
            pnl += (diff/100)
            pnl_after = pnl
            print(date_time, entry, close, diff, pnl_before, pnl_after)
        total_pnl += pnl
        fee = (hits+miss)*70/100
        print(date, pnl, fee, pnl-fee, hits, miss, total_orders)
        return (date, pnl, fee, pnl-fee, hits, miss, len(short_entries))
        #return (date, pnl)
    #return (total_pnl, total_hits, total_miss)
    #return (total_pnl, total_hits, total_miss)

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
        self.hip_lop = Hip_Lop()
    
    def write_kline_log(self, log):
        with open(self.kline_log_file, "a") as f:
            f.write(log + "\r\n")
            f.close()
    
    def feed_series(self, series: pd.Series):
        print(series)
        log = f"{self.df_count},{series['date']},{series['open']},{series['high']},{series['low']},{series['close']},{series['volume']},{series['quote_volume']}"
        self.write_kline_log(log)
        self.df.loc[self.df_count] = series
        self.df_count += 1

        new_orders = self.hip_lop.run_series(series)
        for order in new_orders:
            print(order)
            #size = order[0]
            #price = str(order[1])
            #tp = str(order[2])
    def print_df(self):
        filename = f"{symbol}_{get_date(int(time.time()))}.csv"
        self.df.to_csv(filename)


class Hip_Lop:

    def __init__(self):
        self.short_entries = []
        self.long_entries = []
        self.lev = 100
        #basepath = "/mnt/c/users/rabindar kumar/web/trading/data"
        self.total_orders = 0
        #for day in days:
        #if (day < 10):
        #    day = "0" + str(day)
        #date = f"{year}-{month}-{day}"
        #filepath = f"{basepath}/{year}/{month}/{symbol}/{date}.csv"
        interval = "1m"
        self.interval = int(interval[:-1])

        self.hips = []
        self.lops = []
    
        self.lop_range_movement = (1, 500)
        self.hip_range_movement = (20, 500)
        #range_movement = (10, 500)
        #range_movement = (30, 500)
        #range_movement = (50, 500)
        #range_movement = (1, 500)
        #range_movement = (1, 10000)
        #df = pd.read_csv(filepath)
        #print(df)
        #tm = 300 # target movement
        self.tm = 12000
        #self.win_tm = 1200
        self.win_tm = 800
        #win_tm = 800
        #win_tm = 900
        #win_tm = 1500
        #win_tm = 60 # 2022-12
        #win_tm = 300
        #win_tm = 400
        #win_tm = 500
        #win_tm = 1000
        #win_tm = 800
        self.sm = self.tm/2
        #tm = 300
        #af = 2500
        #af = 300*5
        #af = 1800
        # size = (1/af)/contract_size
        self.af = 300*5
        #self.af = 5000/3
        #self.size = 7 # use af = 5000/3
        #af = 300*0.1 # 2022-12
        #af = 900
        #af = 800
        #fee = 80/af
        self.fee = 0
        self.sl = self.tm/self.af
        self.reward = self.win_tm/self.af
        self.pnl = 0
        self.hits = 0
        self.miss = 0
        self.hip_bars: List[pd.Series] = []
        self.hip_bar_count = 0
        self.lop_bars: List[pd.Series] = []
        self.lop_bar_count = 0
        self.short_entries = []
        self.max_drawdown = 0
        self.short_miss = 0
        self.long_miss = 0
        self.margin = 0
        self.max_margin = 0
        self.stop_long = False
        self.stop_short = False
        #potential_drawdown = 0
        self.pd_date = None
        self.pnl_max = 0
        self.potential_drawdown_max = 0
        self.margin_pdm_max = 0
        self.total_margin = 0
        self.bal_threshold = 0.8
        self.bal_drop_below_threshold = False
        self.started = False
        self.balance = 500

        self.df_count= 0

        self.potential_pnl = 0

        #self.contract_size = 1/10000
        #size = math.floor((1/af)/contract_size)

        self.pd_date = None

        self.contract_size = 1/10000
        self.size = math.floor((1/self.af)/self.contract_size)
        self.af = 1/(self.size*self.contract_size)
        self.sl = self.tm/self.af
        self.reward = self.win_tm/self.af
        print(f"size={self.size}, af={self.af}")

    
    def run_series(self, series: pd.Series):
        close = series['close']
        if (self.fee == 0):
            self.fee = ((close*0.08)/100)/self.af
        date_time = series['date']
        potential_pnl = 0
        entries = self.short_entries.copy()
        for entry in entries:
            diff = close-entry
            if (diff > self.tm):
                self.short_entries.remove(entry)
                self.miss += 1
                self.short_miss += 1
                if (self.short_miss > 18):
                    self.stop_short = True
                self.pnl -= self.sl
                self.margin -= (entry/self.lev)/self.af

            if (diff < -self.win_tm):
                self.short_entries.remove(entry)
                self.hits += 1
                #short_hits += 1
                self.pnl += self.reward
                self.margin -= (entry/self.lev)/self.af
        
        for entry in self.short_entries:
            diff = entry-close
            potential_pnl += (diff/self.af)

            
        entries = self.long_entries.copy()
        for entry in entries:
            diff = close-entry
            if (diff < -self.tm):
                self.long_entries.remove(entry)
                self.miss += 1
                self.long_miss += 1
                if (self.long_miss > 18):
                    self.stop_long = True
                self.pnl -= self.sl
                self.margin -= (entry/self.lev)/self.af
            if (diff > self.win_tm):
                self.long_entries.remove(entry)
                self.hits += 1
                self.pnl += self.reward
                self.margin -= (entry/self.lev)/self.af

        for entry in self.long_entries:
            diff = entry-close
            potential_pnl += (diff/self.af)

        if (potential_pnl < self.potential_drawdown_max):
            self.potential_drawdown_max = potential_pnl
            self.pnl_max = self.pnl
            self.margin_pdm_max = self.margin
            if potential_pnl+self.margin+self.pnl < 0:
                self.drawdown_margin_exceed = True

        if (potential_pnl + self.pnl < self.max_drawdown):
            self.max_drawdown = potential_pnl + self.pnl
            self.pd_date = series['date']
        
        if (potential_pnl+self.pnl < -(self.balance*(1-self.bal_threshold))):
            self.bal_drop_below_threshold = True

        #if (potential_drawdown < -1000):
        #    print(f"max drawdown limit exceeded. month={month}, day={day}, drawdown={pnl+potential_drawdown}")
        #    return (pnl+potential_drawdown, max_drawdown)
        self.potential_pnl = potential_pnl

        self.hip_bars.append(series)
        self.hip_bar_count += 1
        new_orders = []
        if (self.hip_bar_count % 3 == 0):
            h0 = self.hip_bars[0]['high']
            h1 = self.hip_bars[1]['high']
            h2 = self.hip_bars[2]['high']

            if (is_in_range(self.hip_range_movement, h1-h0) and is_in_range(self.hip_range_movement, h1-h2)):
                self.hips.append((self.hip_bars[0], self.hip_bars[1], self.hip_bars[2]))
                entry = self.hip_bars[2]['close']
                #if not stop_short:
                self.short_entries.append(entry)
                new_orders.append((-self.size, entry, entry-self.win_tm))
                self.total_orders += 1
                self.total_margin += (entry/self.lev)/self.af
                self.margin += (entry/self.lev)/self.af
                self.pnl -= self.fee
                #final_short_entries.append(bars[1]['close'])
                #long_entries.append(bars[2]['close'])
                self.hip_bars = self.hip_bars[2:]
                self.hip_bar_count -= 2
            else:
                self.hip_bars = self.hip_bars[1:]
                self.hip_bar_count -= 1

        self.lop_bars.append(series)
        self.lop_bar_count += 1
        if (self.lop_bar_count % 3 == 0):
            l0 = self.lop_bars[0]['low']
            l1 = self.lop_bars[1]['low']
            l2 = self.lop_bars[2]['low']

            if (is_in_range(self.lop_range_movement, l0-l1) and is_in_range(self.lop_range_movement, l2-l1)):
                self.lops.append((self.lop_bars[0], self.lop_bars[1], self.lop_bars[2]))
                #short_entries.append(bars[1]['close'])
                #final_short_entries.append(bars[1]['close'])
                #if not stop_long:
                entry = self.lop_bars[2]['close']
                self.long_entries.append(entry)
                new_orders.append((self.size, entry, entry+self.win_tm))
                self.total_orders += 1
                self.pnl -= self.fee
                self.total_margin += (entry/self.lev)/self.af
                self.margin += (entry/self.lev)/self.af
                self.lop_bars = self.lop_bars[2:]
                self.lop_bar_count -= 2
            else:
                self.lop_bars = self.lop_bars[1:]
                self.lop_bar_count -= 1
        if (self.margin > self.max_margin):
            self.max_margin = self.margin
        self.fee = (close*0.08/100)/self.af
        return new_orders
        #print(self.total_orders)
    #pnl -= (0.7*total_orders)
    #print(pnl, potential_pnl, max_drawdown)
    #print((pnl+potential_drawdown, max_drawdown, pd_date, potential_drawdown, total_orders, hits, miss, len(long_entries), len(short_entries)))
    #print(total_orders, margin, max_margin, potential_drawdown_max, margin_pdm_max, pnl_max, bal_drop_below_threshold)

    def print_result(self):
        print(self.potential_pnl+self.pnl)
        print(self.total_orders, self.margin, self.max_margin, self.potential_drawdown_max, self.margin_pdm_max, self.pnl_max, self.bal_drop_below_threshold)
        #return (pnl+potential_pnl, max_drawdown, miss, hits, short_miss, long_miss, potential_drawdown_max, pnl_max)
        #print(self.pnl, self.potential_pnl, self.max_drawdown)
        #print(self.total_orders, self.hits, self.miss, len(self.long_entries), len(self.short_entries))
        #print((pnl+potential_drawdown, max_drawdown, pd_date, potential_drawdown, total_orders, hits, miss, len(long_entries), len(short_entries)))
        #print(total_orders, margin, max_margin, potential_drawdown_max, margin_pdm_max, pnl_max, bal_drop_below_threshold)
    
    def get_result(self):
        return (self.pnl+self.potential_pnl, self.max_drawdown, self.miss, self.hits, self.short_miss, self.long_miss, self.potential_drawdown_max, self.pnl_max)
    

def hip_lop_live(month, day):
    symbol = "BTCUSDT"
    interval = "1m"
    cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'quote_volume']
    interval = int(interval[:-1])

    max_tries = 5

    hip_lop = Hip_Lop(log_kline=True)
    # run for 2 hours
    total_seconds = 22*60*60
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
                hip_lop.feed_series(series)
            last_time_sec = int(new_klines[-1][0]/1000)
        print(new_klines)
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

class Tester:

    def __init__(self): 
        pass
    
    def test(self, filepath):
        hip_lop = Hip_Lop()
        df = pd.read_csv(filepath)
        for i, series, in df.iterrows():
            #print(series)
            hip_lop.run_series(series)
        hip_lop.print_result()

    '''
    def test(self, basepath, year, month, days):
        for day in days:
            if (day < 10):
                day = "0" + str(day)
            symbol = "BTCUSDT"
            date = f"{year}-{month}-{day}"
            filepath = f"{basepath}/{year}/{month}/{symbol}/{date}.csv"
            self._test(filepath)
    '''



#balance = 500
def hip_lop(month, day, af, balance, filepath=None):
    basepath = "/mnt/c/users/rabindar kumar/web/trading/data"
    if (filepath is None and (month is not None and day is not None)):
        if (day < 10):
            day = "0" + str(day)
        date = f"{year}-{month}-{day}"
        filepath = f"{basepath}/{year}/{month}/{symbol}/{date}.csv"

    if (filepath is None):
        return
    


    total_pnl = 0
    #start = months[month][1]
    #end = months[month][0]
    start = 1
    end = 2
    #while start <= end-3:
    #    dates = [f"{year}-{month}-{get_str(start)}", f"{year}-{month}-{get_str(start+1)}", f"{year}-{month}-{get_str(start+2)}"]
    #    start += 3
    #all_dates = [["2024-12-10"], ["2024-12-11"], ["2024-12-12"], ["2024-12-10", "2024-12-11"], ["2024-12-10", "2024-12-11", "2024-12-12"]]
    #for dates in all_dates:
    '''
    if (filepath is None and (month is not None and day is not None)):
        #for day in days:
        if (day < 10):
            day = "0" + str(day)
        date = f"{year}-{month}-{day}"
        filepath = f"{basepath}/{year}/{month}/{symbol}/{date}.csv"
    elif (filepath is None):
        return
    '''
    #filepath = "sample_data.csv"

    #dates = set()
    #dates.add(open_date)
    #dates.add(close_date)
    #dates = list(dates)
    #dates = [open_date, close_date]
    #dates = ["2024-12-20", "2024-12-21", "2024-12-22"]
    '''
    start_day = 7
    end_day = 9
    dates = []
    while start_day <= end_day:
        if (start_day < 10):
            start_day = "0" + str(start_day)
        date = f"{year}-{month}-{start_day}"
        dates.append(date)
        start_day = int(start_day) + 1
        '''
        #dates = ['2024-12-22']
    short_entries = []
    long_entries = []
    lev = 100
    total_orders = 0

    interval = "1m"
    interval = int(interval[:-1])

    hips = []
    lops = []

    lop_range_movement = (1, 500)
    hip_range_movement = (20, 500)
    #range_movement = (10, 500)
    #range_movement = (30, 500)
    #range_movement = (50, 500)
    #range_movement = (1, 500)
    #range_movement = (1, 10000)
    #df = pd.read_csv(filepath)
    #print(df)
    #tm = 300 # target movement
    tm = 12000
    #win_tm = 1200
    win_tm = 600
    #win_tm = 800
    #win_tm = 900
    #win_tm = 1500
    #win_tm = 60 # 2022-12
    #win_tm = 300
    #win_tm = 400
    #win_tm = 500
    #win_tm = 1000
    #win_tm = 800
    sm = tm/2
    #tm = 300
    #af = 2500
    af = 300*5
    #af = 300*0.1 # 2022-12
    #af = 900
    #af = 800
    #fee = 80/af
    fee = 0
    sl = tm/af
    reward = win_tm/af
    rrf = 2
    pnl = 0
    hits = 0
    miss = 0
    hip_bars: List[pd.Series] = []
    hip_bar_count = 0
    lop_bars: List[pd.Series] = []
    lop_bar_count = 0
    short_entries = []
    max_drawdown = 0
    short_miss = 0
    long_miss = 0
    margin = 0
    max_margin = 0
    stop_long = False
    stop_short = False
    #potential_drawdown = 0
    pd_date = None
    pnl_max = 0
    potential_drawdown_max = 0
    margin_pdm_max = 0
    total_margin = 0
    bal_threshold = 0.8
    bal_drop_below_threshold = False
    started = False
    count = 0
    
    #open_time_sec = get_seconds(open_time)

    #for date in dates:
    #    print(date)
    #    filepath = f"{basepath}/{year}/{month}/{symbol}/{date}.csv"
    df = pd.read_csv(filepath)
    for i, series in df.iterrows():
        
        curr_time = series['date'].split(' ')[1]
        #if (date == open_date and get_seconds(curr_time) < open_time_sec):
        #    continue
        #count += 1
        #if (count % 1 != 0):
        #    continue
        #count = 0
        close = series['close']
        if (fee == 0):
            fee = ((close*0.08)/100)/af
        date_time = series['date']
        potential_pnl = 0
        entries = short_entries.copy()
        for entry in entries:
            diff = close-entry
            if (diff > tm):
                short_entries.remove(entry)
                miss += 1
                short_miss += 1
                if (short_miss > 18):
                    stop_short = True
                pnl -= sl
                margin -= (entry/lev)/af

            if (diff < -win_tm):
                short_entries.remove(entry)
                hits += 1
                #short_hits += 1
                pnl += reward
                margin -= (entry/lev)/af
                #print(f"short hit, entry: {entry}, close: {close}")

        
        for entry in short_entries:
            diff = entry-close
            potential_pnl += (diff/af)

            
        entries = long_entries.copy()
        for entry in entries:
            diff = close-entry
            if (diff < -tm):
                long_entries.remove(entry)
                miss += 1
                long_miss += 1
                if (long_miss > 18):
                    stop_long = True
                pnl -= sl
                margin -= (entry/lev)/af
            if (diff > win_tm):
                long_entries.remove(entry)
                hits += 1
                pnl += reward
                margin -= (entry/lev)/af
                #print(f"long hit, entry: {entry}, close: {close}")

        for entry in long_entries:
            diff = entry-close
            potential_pnl += (diff/af)
        
        if (potential_pnl+pnl < potential_drawdown_max):
        #if (potential_drawdown < potential_drawdown_max):
            potential_drawdown_max = potential_pnl
            pnl_max = pnl
            margin_pdm_max = margin
            if potential_pnl+margin+pnl < 0:
                drawdown_margin_exceed = True

        if (potential_pnl+pnl < max_drawdown):
        #if (potential_drawdown + pnl < max_drawdown):
            max_drawdown = potential_pnl + pnl
            pd_date = series['date']
        
        if (potential_pnl+pnl < -(balance*(1-bal_threshold))):
        #if (potential_drawdown+pnl < -(balance*(1-bal_threshold))):
            bal_drop_below_threshold = True

        #if (potential_drawdown < -1000):
        #    print(f"max drawdown limit exceeded. month={month}, day={day}, drawdown={pnl+potential_drawdown}")
        #    return (pnl+potential_drawdown, max_drawdown)

        hip_bars.append(series)
        hip_bar_count += 1
        if (hip_bar_count % 3 == 0):
            h0 = hip_bars[0]['high']
            h1 = hip_bars[1]['high']
            h2 = hip_bars[2]['high']

            if (is_in_range(hip_range_movement, h1-h0) and is_in_range(hip_range_movement, h1-h2)):
                hips.append((hip_bars[0], hip_bars[1], hip_bars[2]))
                entry = hip_bars[2]['close']
                #if not stop_short:
                short_entries.append(entry)
                total_orders += 1
                total_margin += (entry/lev)/af
                margin += (entry/lev)/af
                pnl -= fee
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
                #short_entries.append(bars[1]['close'])
                #final_short_entries.append(bars[1]['close'])
                #if not stop_long:
                entry = lop_bars[2]['close']
                long_entries.append(entry)
                total_orders += 1
                pnl -= fee
                total_margin += (entry/lev)/af
                margin += (entry/lev)/af
                lop_bars = lop_bars[2:]
                lop_bar_count -= 2
            else:
                lop_bars = lop_bars[1:]
                lop_bar_count -= 1
        if (margin > max_margin):
            max_margin = margin
        fee = (close*0.08/100)/af
        #if (date == close_date and get_seconds(curr_time) > get_seconds(close_time)):
        #    print(f'closing at {close_date} {close_time}')
        #    break
    #pnl -= (0.7*total_orders)
    #print(pnl, potential_pnl, max_drawdown)
    #print((pnl+potential_drawdown, max_drawdown, pd_date, potential_drawdown, total_orders, hits, miss, len(long_entries), len(short_entries)))
    total_pnl += potential_pnl+pnl
    print(potential_pnl+pnl)
    print(total_orders, margin, max_margin, potential_drawdown_max, margin_pdm_max, pnl_max, bal_drop_below_threshold)
    return (pnl+potential_pnl, max_drawdown, miss, hits, short_miss, long_miss, potential_drawdown_max, pnl_max)
    '''
    for entry in short_entries:
        diff = entry-close
        if (diff < 0):
            hits += 1
        else:
            miss += 1
        pnl += (diff/100)
        pnl_before = pnl
        pnl += (diff/100)
        pnl_after = pnl
        print(date_time, entry, close, diff, pnl_before, pnl_after)
    total_pnl += pnl
    fee = (hits+miss)*70/100
    print(date, pnl, fee, pnl-fee, hits, miss, total_orders)
    return (date, pnl, fee, pnl-fee, hits, miss, len(short_entries))
    '''
    #print(total_pnl)
    #return (date, pnl)
#return (total_pnl, total_hits, total_miss)
#return (total_pnl, total_hits, total_miss)



'''
info = {}
for month in months:
    start = months[month][1]
    end = months[month][0]
    days = []
    while start <= end:
        days.append(start)
        start += 1
    info[month] = hip(month, days)

print(info)
'''

'''
for month in months:
    start = months[month][1]
    end = months[month][0]
    days = []
    while start <= end:
        days.append(start)
        start += 1

    total_pnl = 0
    for day in days:
        new_days = [day]
        #hip_lop(month, new_days)
        
        (date, pnl, fee, net_pnl, hits, miss, remain) = hip(month, new_days)
        print(f"hip: {date}, {pnl}, {fee}, {net_pnl}, {hits}, {miss}, {remain}")
        total_pnl += net_pnl
        (date, pnl, fee, net_pnl, hits, miss, remain) = lop(month, new_days)
        print(f"lop: {date}, {pnl}, {fee}, {net_pnl}, {hits}, {miss}, {remain}")
        total_pnl += net_pnl

    log = f"date: {year}-{month}, pnl={total_pnl}"
    with open("log.txt", "a") as f:
        f.write(log + "\r\n")
        f.close()
'''  

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

def hip_lop_exec():
    #balance = 5000
    df = 600
    #df = 1250
    bal_incr = 1000
    month_list = list(months.keys())
    #month_list.sort()
    month_list = ["12"]
    balance = 500
    basepath = "/mnt/c/users/rabindar kumar/web/trading/data"

    hip_lop_obj = Hip_Lop()

    result_df: pd.DataFrame = pd.DataFrame([], columns=['date', 'pnl'])
    result_df_count = 0

    for month in month_list:
        start = months[month][1]
        end = months[month][0]
        days = []
        while start <= end:
            days.append(start)
            start += 1
        
        total_miss = 0
        total_hits = 0
        total_pnl = 0
        md = -50

        holding = 1
        skip = holding
        for day in days:
            if day < 10:
                day = "0" + str(day)
            
            date = f"{year}-{month}-{day}"
            filepath = f"{basepath}/{year}/{month}/{symbol}/{date}.csv"
            if (skip == 0):
                hip_lop_obj = Hip_Lop()
                skip = holding
            df = pd.read_csv(filepath)
            
            for i, series in df.iterrows():
                hip_lop_obj.run_series(series)
            
            hip_lop_obj.print_result()
            skip -= 1
            if (skip > 0):
                continue
            (pnl, max_drawdown, miss, hits, short_miss, long_miss, potential_drawdown_max, pnl_max) = hip_lop_obj.get_result()
            result_df.loc[result_df_count] = pd.Series(data=[date, pnl], index=['date', 'pnl'])
            result_df_count +=1
            '''
            new_days = [day]
            #hip_lop(month, new_days)
            
            (date, pnl, fee, net_pnl, hits, miss, remain) = hip(month, new_days)
            print(f"hip: {date}, {pnl}, {fee}, {net_pnl}, {hits}, {miss}, {remain}")
            total_pnl += net_pnl
            (date, pnl, fee, net_pnl, hits, miss, remain) = lop(month, new_days)
            print(f"lop: {date}, {pnl}, {fee}, {net_pnl}, {hits}, {miss}, {remain}")
            total_pnl += net_pnl

        log = f"date: {year}-{month}, pnl={total_pnl}"
        with open("log.txt", "a") as f:
            f.write(log + "\r\n")
            f.close()
            '''
            '''
            if (balance - bal_incr > 5000):
                if (df > 100):
                    df -= 50
                    bal_incr += 700
                elif (df <= 100):
                    df -= 10
                    bal_incr += 700
                if (df < 50):
                    df = 50
                if (bal_incr > 10000):
                    bal_incr = 10000
            else:
                df = 1250
                bal_incr = 1000
            '''
            #tester = Tester()
            #tester.test(basepath, year, month, [day])
            #(pnl, potential_pnl, max_drawdown) = tester.get_result()
            #(pnl, max_drawdown, miss, hits, short_miss, long_miss, potential_drawdown_max, pnl_max) = hip_lop(month, day, df, balance)
            
            #if (skip > 0):
            #    (pnl, max_drawdown, miss, hits, short_miss, long_miss, potential_drawdown_max, pnl_max) = hip_lop_obj.get_result()

            if (max_drawdown < md):
                md = max_drawdown
            total_miss += miss
            total_hits += hits
            balance += pnl
            total_pnl += pnl
            date=f"{year}-{month}-{day}"
            print(f"date={date} {get_day_name(date)}, pnl={pnl}, balance={balance} max_drawdown={max_drawdown} pdm={potential_drawdown_max}, pnl_max={pnl_max}, miss={miss}, hits={hits}")
        if (skip > 0):
            (pnl, max_drawdown, miss, hits, short_miss, long_miss, potential_drawdown_max, pnl_max) = hip_lop_obj.get_result()
            result_df.loc[result_df_count] = pd.Series(data=[date, pnl], index=['date', 'pnl'])
            result_df_count +=1
            if (max_drawdown < md):
                md = max_drawdown
            total_miss += miss
            total_hits += hits
            balance += pnl
            total_pnl += pnl
            date=f"{year}-{month}-{day}"
            print(f"date={date} {get_day_name(date)}, pnl={pnl}, balance={balance} max_drawdown={max_drawdown} pdm={potential_drawdown_max}, pnl_max={pnl_max}, miss={miss}, hits={hits}")
        print(f"date={year}-{month}, pnl={total_pnl}, balance={balance} max_drawdown={md}, miss={total_miss}, hits={total_hits}")
        print(result_df)
        result_df.to_csv("pnl.csv")
        #lop(month, new_days)
        
    #date = "2024-12-11"

    #hip_lop("12", 1)

hip_lop_exec()
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