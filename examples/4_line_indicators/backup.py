def atr(interval, min_tr, month, days, month_days: dict):
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
    item = None
    flag = True
    arc = 0
    constant_c = 3.2
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

    months = [int(item) for item in list(month_days.keys())]
    months.sort()
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
                    ser = pd.Series(data = [date, open_p, high, low, close, volume, quote_volume, weighted_value], index = ["date", "open", "high", "low", "close", "volume", "quote_volume", "weighted_value"])
                    #print(ser)
                    if (len(data) + 1 > max_entries):
                        start = data.index[0]
                        data = data.truncate(before=start+1, after=df_count)
                    a = ser['high'] - ser['close']
                    if (item == None):
                        tr.append(a)
                        item = {'high': ser['high'], 'low': ser['low'], 'close': ser['close']}
                        sub_df_count = 0
                        continue



                    #if (tr_count == 0):
                    #    tr.append(a)
                    #    tr[tr_count] = a
                    #else:
                    #item = data.loc[data.index[-1]]
                    b = abs(item['close'] - ser['high'])
                    c = abs(item['close'] - ser['low'])
                    if (flag):
                        tr.append(get_tr(a, b, c))
                        if (len(tr) == min_tr):
                            print(tr)
                            flag = False
                            atr = statistics.mean(tr)
                            print(tr, len(tr), atr)
                            arc = constant_c*atr
                            print(arc)
                    else:
                        atr = ((min_tr-1)*atr + get_tr(a, b, c)) / min_tr
                        arc = constant_c*atr
                        print(arc)
                    sub_df_count = 0
                    item = {'high': ser['high'], 'low': ser['low'], 'close': ser['close']}
                    #print(ser['date'], atr, arc, flag)
                    '''
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
                    '''

    return arc