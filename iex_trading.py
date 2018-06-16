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
from constants import Constants
from pandas.io.json import json_normalize
from data_managers.earnings_manager import EarningsManager

class IEXTrading(object):
    #paths and filenames
    PATH_CACHE           = "cache/"
    PATH_SYMBOLS         = "symbols/"
    FILENAME_METADATA    = "meta.txt"
    FILENAME_MARKET_DATA = "market_data.csv"
    FILENAME_NASDAQ      = "nasdaq.csv"
    FILENAME_NYSE        = "nyse.csv"
    FILENAME_AMEX        = "amex.csv"

    #constants
    API_URL_IEX = "https://api.iextrading.com/1.0"
    BATCH_LIMIT_IEX = 100
    MAX_MARKET_DATA_AGE_MINUTES = 120
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    # JSON data parsing methods
    def _parse_quote(symbol, data):
        #pprint(data)
        quote = data[Constants.DataType.QUOTE.value]
        #pprint(quote)
        series = pd.Series(quote)
        #print(series)
        print("quote")
        return series

    def _parse_earnings(symbol, data):
        print("earnings")
        intermediate = data[Constants.DataType.EARNINGS.value]
        if not intermediate:
            return None
        earnings = intermediate[Constants.DataType.EARNINGS.value]

        # Index Levels
        indices = [(symbol, "-"+str(i+1)+"q") for i in range(len(earnings))]
        hier_index = pd.MultiIndex.from_tuples(indices)
        #for quarter in earnings:
            #quarter.update({"symbol":symbol})
        #pprint(earnings)
        #print(hier_index)
        df = pd.DataFrame(earnings, hier_index)
        #print(df)
        #df["symbol"] = symbol
        #df.set_index("symbol", append=True, inplace=True)
        #series.set_index(["symbol"], inplace=True)
        print(df)
        return df
        #TODO: concat all of these dataframes somewhere

    def _parse_financials(symbol, data):
        print("financials")
        intermediate = data[Constants.DataType.FINANCIALS.value]
        if not intermediate:
            return None
        financials = intermediate[Constants.DataType.FINANCIALS.value]
        #print(intermediate)
        #pprint(financials)
        series = pd.DataFrame(financials)

        #print(series)
        return series

    def _parse_stats(symbol, data):
        print("stats")
        pass

    def _parse_company(symbol, data):
        print("company")
        pass

    MARKET_DATA_TYPES = [(Constants.DataType.QUOTE.value, _parse_quote),
                         (Constants.DataType.EARNINGS.value, _parse_earnings),
                         (Constants.DataType.FINANCIALS.value, _parse_financials),
                         (Constants.DataType.KEY_STATS.value, _parse_stats),
                         (Constants.DataType.COMPANY.value, _parse_company),
                        ]

    def __init__(self):
        self.earnings_manager = EarningsManager()


        self.symbols = self._read_symbols()
        self.market_data = self._read_market_data()
        #self.sp500 = self.get_sp500()
        #print(self.best_peratio())


        #stats
        #df = self.stats(symbols)

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
        http_req = "/" + Constants.DataType.STOCK.value + "/" + symbol + "/" + Constants.DataType.COMPANY.value
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

    def _api_request_time_series(self, symbols, range):
        dfs = []
        for symbol in symbols:
            request_base = ("/" + Constants.DataType.STOCK.value + "/" + symbol + "/" +
                            Constants.DataType.CHART.value + "/" + range)
            response = requests.get(url=self.API_URL_IEX + request_base)
            series_list = [pd.Series(day) for day in response.json()]
            df = pd.concat(series_list, axis=1).transpose()
            dfs.append(df)
        return dfs

    def _api_request_market_data(self):
        symbol_batches = list(Utils.chunks(self.symbols, self.BATCH_LIMIT_IEX))
        request_base = ("/" + Constants.DataType.STOCK.value + "/" + Constants.DataType.MARKET.value + "/" +
                        Constants.DataType.BATCH.value + "?")
        series_list = []
        print("Requesting market data through API...")
        json_collection = {}
        types = ",".join([i[0] for i in self.MARKET_DATA_TYPES])
        print(types)
        for batch in symbol_batches:
            #set up the parameters for API request
            params = dict(
                symbols = ','.join(batch),
                types = types
            )
            response_json = requests.get(url=self.API_URL_IEX + request_base, params=params).json()
            #this JSON object will make a fine addition to my collection
            #json_collection = {**json_collection, **response_json}

            #results = {data_type : response_json[data_type] for data_type in self.MARKET_DATA_TYPES}
            #call each parsing function
            #pprint(response_json.items())
            for symbol, data in response_json.items():
                self.earnings_manager.add_symbol(symbol, data)
            #    for i in range(len(self.MARKET_DATA_TYPES)):
            #        series_list.append(self.MARKET_DATA_TYPES[i][1](symbol, data))

            #for k,v in response.json().items():
                #for qk, val in v.items():
                    #ser = pd.Series(val)
                    #series_list.append(ser)
        #df = pd.concat(series_list, axis=1).transpose()
        #df.set_index("symbol", inplace=True)
        #print("Done!")
        #pprint(json_collection)
        self.earnings_manager.create_df()

        #return df





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

    def nasdaq_dozen(self):
        pass
        #1: Is revenue increasing?
        #2: Is EPS (Earnings Per Share) increasing?
        #3: Is ROE (Return On Equity) increasing for 2 years?
        #4: Analyst recommendations
        #5: PEG ratio
        #6: Is the company earning more than the industry average?
        #7: Is Days to Cover less than 2?
        #8: Is the net activity positive (more buyers than sellers) over the last 3 months?

    def plot():
        symbols = ["GOOG", "AMZN"]
        dfs = self._api_request_time_series(symbols, "ytd")
        #for df in dfs:
        #    df["date"] = pd.to_datetime(df["date"])
        #    df.plot(x="date", y="close")
        #df_apple_ts["date"] =  pd.to_datetime(df_apple_ts["date"])
        #df_apple_ts.plot(x="date", y="close")
        #plt.show()

        fig, ax = plt.subplots()
        for i, df in enumerate(dfs):
            df["date"] = pd.to_datetime(df["date"])
            df.plot(ax=ax, x="date", y="close", label=symbols[i])

        plt.ylabel("Share price (dollars)")
        plt.xlabel("Date")
        plt.title("Share Price over Time")
        plt.show()

    def stats(self, symbols):
        series_list = []
        for symbol in symbols:
            request_base = "/stock/" + symbol + "/stats"
            response = requests.get(url=self.API_URL_IEX + request_base)
            data = response.json()
            data.update({"symbol":symbol})
            series_list.append(pd.Series(data))
        df = pd.concat(series_list, axis=1).transpose()
        print(df)
        return df
