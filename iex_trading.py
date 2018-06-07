import requests
from pprint import pprint
from utils import Utils
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import sys
import csv
from bs4 import BeautifulSoup

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
    MAX_MARKET_DATA_AGE_MINUTES = 120
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    TIME_SERIES_RANGE = ["5y",   #historically adjusted market-wide data
                         "2y",   #^
                         "ytd",  #^
                         "6m",   #^
                         "3m",   #^
                         "1m",   #^
                         "1d",   #IEX-only data by minute
                         "date", #IEX-only data by minute for a specified date
                                 #in the format YYYYMMDD (e.g., /date/19970408)
                         "dynamic", #returns 1d or 1m data depending on the day
                                    #or week and time of day. Intraday per minute
                                    #data is only returned during market hours.
                        ]

    def __init__(self):
        self.symbols = self._read_symbols()
        self.market_data = self._read_market_data()
        self.sp500 = self.get_sp500()
        print(self.best_peratio())
        df_apple_ts = self._api_request_time_series("AAPL", "2y")
        df_apple_ts["date"] =  pd.to_datetime(df_apple_ts["date"])
        df_apple_ts.plot(x="date", y="close")
        plt.show()

    def _read_symbols(self):
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

    def cache_refresh(self):
        self.market_data = _api_request_market_data()

    def company_info(self, symbol):
        http_req = "/stock/" + symbol + "/company"
        response = requests.get(self.API_URL_IEX + http_req)
        json = response.json()
        df = json_normalize(json)
        pprint(json)
        print(df)

    def _save_market_data(self, df):
        try:
            df.to_csv(self.PATH_CACHE + self.FILENAME_MARKET_DATA)
            with open(self.PATH_CACHE + self.FILENAME_METADATA, "w+") as f_meta:
                f_meta.write(datetime.now().strftime(self.DATETIME_FORMAT) + "\n")
                f_meta.write("Data collected from IEX Trading API\n")
                f_meta.write("Do not change this file!\n")
            print("Market data successfully saved to " + self.PATH_CACHE + self.FILENAME_MARKET_DATA)
        except OSError as err:
            print("OSError: {0}".format(err))
            raise

    def _read_market_data(self):
        #determine if cached data is still fresh
        try:
            with open(self.PATH_CACHE + self.FILENAME_METADATA, "r") as f_meta:
                #max_age = MAX_DATA_AGE_MINUTES minutes ago
                max_age = datetime.now() - (datetime.now() -
                            timedelta(minutes=self.MAX_MARKET_DATA_AGE_MINUTES))
                data_age = (datetime.now() -
                            datetime.strptime(f_meta.readline().rstrip('\n'), self.DATETIME_FORMAT))
                if data_age > max_age:
                    #stale data...
                    print("Stale data...")
                    return self._api_request_market_data()
                else:
                    #fresh data!
                    print("Fresh data...\nReading cached market data...")
                    return pd.read_csv(self.PATH_CACHE + self.FILENAME_MARKET_DATA)
        except OSError as err:
            #it's likely that the metadata file hasn't been created yet
            print("Caught OSError: {0}".format(err))

            return self._api_request_market_data()

    def _api_request_time_series(self, symbol, range):
        request_base = "/stock/" + symbol + "/chart/" + range
        response = requests.get(url=self.API_URL_IEX + request_base)
        series_list = [pd.Series(day) for day in response.json()]
        df = pd.concat(series_list, axis=1).transpose()
        #df.set_index("date", inplace=True)
        print(df)
        return df

    def _api_request_market_data(self):
        symbol_batches = list(Utils.chunks(self.symbols, self.BATCH_LIMIT_IEX))
        request_base = "/stock/market/batch?"
        series_list = []
        print("Requesting market data through API...")
        for batch in symbol_batches:
            #set up the parameters for API request
            params = dict(
                symbols = ','.join(batch),
                types = "quote"
            )
            response = requests.get(url=self.API_URL_IEX + request_base, params=params)
            for k,v in response.json().items():
                for qk, val in v.items():
                    ser = pd.Series(val)
                    series_list.append(ser)
        df = pd.concat(series_list, axis=1).transpose()
        df.set_index("symbol", inplace=True)
        print("Done!")
        self._save_market_data(df)
        return df

    def get_sp500(self):
        #grab a list of the current S&P 500 symbols (tickers) from Wikipedia
        response = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        soup = BeautifulSoup(response.text, 'lxml')
        table = soup.find('table', {'class': 'wikitable sortable'})
        symbols = []
        for row in table.findAll('tr')[1:]:
            symbol = row.findAll('td')[0].text
            symbols.append(symbol)
        return sorted(symbols)

    def best_peratio(self):
        #TODO: don't change the data
        print(self.market_data)
        self.market_data["peRatio"] = self.market_data["peRatio"].astype(float)
        print(self.market_data)
        return self.market_data.nsmallest(n=50, columns="peRatio", keep="first")[["companyName", "latestPrice", "latestTime", "latestSource"]]
        #wtf, -1556444031219243500 for Groupon???
