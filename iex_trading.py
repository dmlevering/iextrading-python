import requests
from pprint import pprint
from utils import Utils
from stock import Stock
import numpy as np
import pandas as pd
import datetime
import sys
import csv

class IEXTrading(object):
    #paths and filenames
    PATH_CACHE = "cache/"
    PATH_SYMBOLS = "symbols/"
    FILENAME_METADATA = "meta.txt"
    FILENAME_MARKET_DATA = "market_data.csv"
    FILENAME_NASDAQ = "nasdaq.csv"
    FILENAME_NYSE = "nyse.csv"
    FILENAME_AMEX = "amex.csv"

    #constants
    API_URL_IEX = "https://api.iextrading.com/1.0"
    BATCH_LIMIT_IEX = 100
    MAX_DATA_AGE_MINUTES = 5
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S\n"


    def __init__(self):
        self.symbols = self.read_symbols()
        self.market_data = self.read_market_data()
        pass

    def read_symbols(self):
        symbols = set()
        with open(self.PATH_SYMBOLS + self.FILENAME_NASDAQ, "r") as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                symbols.add(row[0])
        with open(self.PATH_SYMBOLS + self.FILENAME_NYSE, "r") as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                symbols.add(row[0])
        with open(self.PATH_SYMBOLS + self.FILENAME_AMEX, "r") as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                symbols.add(row[0])
        return sorted(list(symbols))

    def api_call(self, params):
        response = requests.get(url=self.API_URL_IEX, params=params)
        json_response = response.json()
        return json_response

    def company_info(self, symbol):
        http_req = "/stock/" + symbol + "/company"
        response = requests.get(self.API_URL_IEX + http_req)
        json = response.json()
        df = json_normalize(json)
        pprint(json)
        print(df)

    def save_market_data(self, df):
        try:
            df.to_csv(self.PATH_CACHE + self.FILENAME_MARKET_DATA)
            with open(self.PATH_CACHE + self.FILENAME_METADATA, "w+") as f_meta:
                f_meta.write(datetime.datetime.now().strftime(self.DATETIME_FORMAT))
                f_meta.write("Data collected from IEX Trading API\n")
                f_meta.write("Do not change this file!\n")
        except OSError as err:
            print("OSError: {0}".format(err))
            raise

    def read_market_data(self):
        #determine if cached data is still fresh
        try:
            with open(self.PATH_CACHE + self.FILENAME_METADATA, "r") as f_meta:
                #MAX_DATA_AGE_MINUTES minutes ago
                max_age = datetime.datetime.now() - (datetime.datetime.now() -
                            datetime.timedelta(minutes=self.MAX_DATA_AGE_MINUTES))
                data_age = (datetime.datetime.now() -
                            datetime.datetime.strptime(f_meta.readline(), self.DATETIME_FORMAT))
                if data_age > max_age:
                    #stale data...
                    print("Stale data; requesting market data through API...")
                    return self._api_request_market_data()
                else:
                    #fresh data!
                    print("Fresh data; reading cached market data...")
                    return pd.read_csv(self.PATH_CACHE + self.FILENAME_MARKET_DATA)
        except OSError as err:
            print("OSError: {0}".format(err))
            print("Requesting market data through API...")
            return self._api_request_market_data()



    def _api_request_market_data(self):
        batches = list(Utils.chunks(self.symbols, 100))
        base = "/stock/market/batch?"
        series = []
        for chunk in batches:
            #set up the parameters for our API request
            params = dict(
                symbols = ','.join(chunk),
                types = "quote" #price,ohlc,stats,
            )
            response = requests.get(url=self.API_URL_IEX + base, params=params)
            json = response.json()
            for k,v in json.items():
                for qk, val in v.items():
                    ser = pd.Series(val)
                    series.append(ser)
        df = pd.concat(series, axis=1).transpose()
        df.set_index("symbol", inplace=True)
        #print(df)
        print("Done!")
        self.save_market_data(df)
        return df

    def best_peratio(self, df):
        print(df.dtypes)
        df["peRatio"] = df["peRatio"].astype(float)
        return df.nsmallest(n=50, columns="peRatio", keep="first")[["companyName", "latestPrice", "latestTime", "latestSource"]]
        #wtf, -1556444031219243500 for Groupon???
