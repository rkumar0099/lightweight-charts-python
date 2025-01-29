import os
import requests
import time
import pandas as pd
from typing import List, Dict

alphabets: List[str] = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", 
                        "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

date: str = "2024-11-25"
exchange: str = "gateio"

exchange_keys: Dict[str, Dict[str, str]] = {"symbol": {"binance": "symbol", "gateio": "currency_pair"},
                                            "volume": {"binance": "volume", "gateio": "quote_volume"}}

def symbol(obj: dict):
    return obj[exchange_keys['symbol'][exchange]]

def volume(obj: dict):
    return float(obj[exchange_keys['volume'][exchange]])

assets: List[str] = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'BCHUSDT', 'SOLUSDT', 'ALGOUSDT', 'LTCUSDT', 
'ETCUSDT', 'LINKUSDT', 'DOGEUSDT', 'PEPEUSDT']

def ticker_params():
    window_size = "1m"
    symbols: str = ''
    for symbol in assets:
        symbols += f'"{symbol}",'
    symbols = '[' + symbols[:-1] + ']'
    #print(symbols)
    #return {"symbols": symbols, "windowSize": window_size}
    params: str = f"symbols={symbols}&windowSize={window_size}"
    return params

def initialize():
    header: str = ",timestamp,open,high,low,close,base_volume,quote_volume"
    if not os.path.isdir(f'./data/{date}'):
        os.mkdir(f"./data/{date}")
    for symbol in assets:
        path: str = f"./data/{date}/{symbol}.csv"
        if not (os.path.isfile(path)):
            with open(path, "w") as f:
                f.write(header + "\r\n")
            f.close()

def test_csv():
    path: str = f"./data/{date}/ALGOUSDT.csv"
    df = pd.read_csv(path)
    print(df.index.str)
    idx = df['high'] > 0.30
    #print(idx)
    #print(df.loc[idx, ['low', 'close']])
    #print(df.shape[0])
    #print(df.columns)
    #print(len(df['high']))
    #print(df['high'].value_counts().fillna(0))

def insert_data(obj: dict):
    symbol: str = obj['symbol']
    timestamp: int = obj['closeTime']
    open_p: float = obj['openPrice']
    high_p: float = obj['highPrice']
    low_p: float = obj['lowPrice']
    close_p: float = obj['lastPrice']
    base_volume: float = obj['volume']
    quote_volume: float = obj['quoteVolume']

    path: str = f"./data/{date}/{symbol}.csv"
    if not os.path.isfile(path):
        return
    df = pd.read_csv(path)
    index = df.shape[0]
    data: str = f"{index},{timestamp},{open_p},{high_p},{low_p},{close_p},{base_volume},{quote_volume}"
    with open(path, "a") as f:
        f.write(data + "\r\n")
        f.close()

def sleep(duration: int):
    count_time: float = time.monotonic() + duration
    while (count_time - time.monotonic()) > 0:
        continue

def spot_tickers():
    count: int = 86400
    host = "https://api.binance.com"
    prefix = "/api/v3"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    url = f'/ticker'
    query_param = ticker_params()
    url += f"?{query_param}"
    #query_param = {"symbols": assets, "windowSize": "1m"}
    #r = requests.request('GET', host + prefix + url, params=query_param, headers=headers).json()
    start_time: float = 0
    end_time: float = time.monotonic()
    while count > 0:
        end_time = time.monotonic()
        if (end_time-start_time>60):
            try:
                r = requests.request('GET', host + prefix + url, headers=headers).json()
            except Exception as exc:
                print(exc)
                sleep(5)
                continue
            #insert_data(r)
            #index: int = -1
            for obj in r:
                insert_data(obj)
            #obj: dict = r[index]
            #insert_data(obj)
            '''
            symbol: str = obj['symbol']
            open_price: float = obj['openPrice']
            high_price: float = obj['highPrice']
            low_price: float = obj['lowPrice']
            close_price: float = obj['lastPrice']
            base_volume: float = obj['volume']
            quote_volume: float = obj['quoteVolume']
            timestamp: int = obj['closeTime']
            '''
            #open_time: int = r[index]['openTime']
            #close_time: int = r[index]['closeTime']
            #volume: float = r[index]['volume']
            #print(r)
            #print(f'symbol: {symbol}, open_time: {open_time}, close_time: {close_time}, timestamp: {time.time()}, volume: {volume}')
            start_time = time.monotonic()
            count -= 1
            #r[0]['closeTime']

    '''
    for obj in r:
        if (symbol(obj).find("USDT") > -1):
            #print(obj)
            if (volume(obj) > 500000):
                print(obj)
    '''

def future_ticker(symbol, limit=1500):
    symbols = ["BTCUSDT"]
    #limit = 240
    interval = "1m"
    '''
    symbols_arr_str: str = ''
    for symbol in symbols:
        symbols_arr_str += f'"{symbol}",'
    symbols_arr_str = '[' + symbols_arr_str[:-1] + ']'
    '''
    #print(symbols)
    #return {"symbols": symbols, "windowSize": window_size}
    #params: str = f"symbol={symbols}&interval={interval}&limit={limit}"
    params: str = f"symbol={symbol}&interval={interval}&limit={limit}"
    #print(params)

    host = "https://fapi.binance.com"
    prefix = "/fapi/v1/klines"
    url = prefix + "?" + params
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    try:
        r = requests.request('GET', host + url, headers=headers).json()
        return r
    except Exception as exc:
        print(exc)

    return None
    



#move_files()
#fetch_contracts()
#find_longs()
#find_shorts()
#initialize()
#spot_tickers()
#ticker_params()
#test_csv()
#future_ticker("BTCUSDT")