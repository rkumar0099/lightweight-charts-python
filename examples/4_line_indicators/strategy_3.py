import time
import hashlib
import hmac
import json
import requests
import pandas as pd
from test_3 import get_filepath

api_key=''
secret=''


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


class Trade:
    def __init__(self, side, entry, open_time):
        self.side = side
        self.entry = entry
        self.open_time = open_time
        self.close_time = None
        self.exit = None
        self.done = False

    def close(self, exit, close_time):
        self.exit = exit
        self.close_time = close_time
    
    def __str__(self):
        return f"side={self.side}, entry={self.entry}, open_time={self.open_time}, exit={self.exit}, close_time={self.close_time}"


long = 0
short = 0

short_win = 0
long_win = 0
short_loss = 0
long_loss = 0
skip = 0
#arc = 0.0022000
arc = 700
current_price = 0
year = "2024"

months = [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]

trades = [None, None]
trades_completed = []
loss_trades = []
#days = [22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 
#        6, 5, 4, 3, 2, 1]
days = [28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 
        6, 5, 4, 3, 2, 1]
#days = [1, 2, 3]

symbol = "BTCUSDT"
#for month in months:
for day in days:
    #arc = 0
    filepath = get_filepath(symbol, year, month=12, day=day)
    df = pd.read_csv(filepath)
    for i, series in df.iterrows():
        #if (arc == 0):
        #    arc = 0.20/100 * series['open']

        if (skip > 0):
            skip -= 1
            continue

        if (current_price == 0):
            current_price = series['close']
            continue

        if (long == 0 and series['close'] - current_price < -arc):
            long = 1
        
        if (long == 1 and series['close'] - current_price < -2*arc):
            long_loss += 1
            long = 0
            skip = 120
            current_price = 0

        if (long == 1 and series['close'] > current_price):
            long_win += 1
            long = 0

        '''
        if (current_price == 0):
            current_price = series['close']
            long = 1
            trades[0] = Trade("long", current_price, series['date'])
            short = 1
            trades[1] = Trade("short", current_price, series['date'])
            continue

        
        if (short == 1 and series['close'] - current_price < -arc):
            short = 0
            short_win += 1
            trade = trades[1]
            trade.exit = series['close']
            trade.close_time = series['date']
            trades_completed.append(trade)
            trades[1] = None

        if (short == 0 and series['close'] > current_price):
            trades[1] = Trade("short", series['close'], series['date'])
            short = 1

        if (long == 1 and series['close'] - current_price > arc):
            long = 0
            long_win += 1
            trade = trades[0]
            trade.exit = series['close']
            trade.close_time = series['date']
            trades_completed.append(trade)
            trades[0] = None
        
        if (long == 0 and series['close'] < current_price):
            trades[0] = Trade("long", series['close'], series['date'])
            long = 1

        if (short == 1 and series['close'] > current_price+2*arc):
            short_loss += 2
            short = 0
            current_price = 0
            skip = 120
            trade = trades[1]
            trade.exit = series['close']
            trade.close_time = series['date']
            loss_trades.append(trade)
            trades[1] = None
        
        if (long == 1 and series['close'] < current_price-2*arc):
            long_loss += 2
            long = 0
            current_price = 0
            skip = 120
            trade = trades[0]
            trade.exit = series['close']
            trade.close_time = series['date']
            loss_trades.append(trade)
            trades[0] = None
        '''
    #print(month, long_win, short_win, long_loss, short_loss, arc)
print(long_win, short_win, long_loss, short_loss, arc)
net_long_wins= long_win-long_loss
net_short_wins= short_win-short_loss

print(f"total_wins={net_long_wins+net_short_wins}")
#print(trades_completed, loss_trades)
'''
for trade in trades_completed:
    print(trade)

print("\n\n")

for trade in loss_trades:
    print(trade)
'''


