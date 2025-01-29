import os

from zipfile import ZipFile

basepath = "/mnt/c/users/rabindar kumar"
src_path = f"{basepath}/downloads"
dst_path = f"{basepath}/web/trading/data"
months = ["12", "11", "10", "09", "08"]
assets = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'BCHUSDT', 'SOLUSDT', 'ALGOUSDT', 'LTCUSDT', 
'ETCUSDT', 'LINKUSDT', 'DOGEUSDT', 'PEPEUSDT', 'WIFUSDT', 'AVAXUSDT', 'GRTUSDT']

'''
def create_dirs():
    os.mkdir(f"{dst_path}/2024")
    for month in months:
        os.mkdir(f"{dst_path}/2024/{month}")
        for symbol in assets:
            os.mkdir(f"{dst_path}/2024/{month}/{symbol}")
    #os.mkdir(f"{dst_path}/2024/12")
    #os.mkdir(f"{dst_path}/2024/11")
    #os.mkdir(f"{dst_path}/2024/10")
    #os.mkdir(f"{dst_path}/2024/09")
    #os.mkdir(f"{dst_path}/2024/08")

    #print(dst_path)
'''

basepath = "/mnt/c/users/rabindar kumar"
src_path = f"{basepath}/downloads"
data_path = f"{basepath}/web/trading/data"

def extract_file(file_symbol, date, symbol):
    interval = "1m"
    year = date.split("-")[0]
    month = date.split("-")[1]
    filename = f"{file_symbol}_PERP-{interval}-{date}"
    print(filename)

    src_file = f"{src_path}/{filename}.zip"
    dst_path = f"{data_path}/{year}/{month}/{symbol}"

    with ZipFile(src_file) as zip_obj:
        zip_obj.extractall(f"{dst_path}")
    
    os.rename(f"{dst_path}/{filename}.csv", f"{dst_path}/{date}.csv")

#print(symbol)

#filename 

#ALGOUSD_PERP-1m-2024-12-06

#with open()

symbol = "ALGOUSDT"
year = "2024"
month = "12"
#days = ["13", "12", "11", "10", "09", "08", "07", "06"]
days = ["05", "04", "03", "02", "01"]
#days = ["30", "29", "28", "27", "26", "25", "24", "23", "22", "21", "20", "19", "18", "17", "16", 
#        "15", "14", "13", "12", "11", "10", "09", "08", "07", "06", "05", "04", "03", "02", "01"]
for day in days:
    date = f"{year}-{month}-{day}"
#date = "2024-12-13"
    extract_file(symbol.replace("USDT", "USD"), date, symbol)


#create_dirs()