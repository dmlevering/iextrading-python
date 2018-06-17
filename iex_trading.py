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
from pandas.io.json import json_normalize
from cache.cache import Cache
from data.data_manager import DataManager

class IEXTrading(object):
    #constants
    API_URL_IEX = "https://api.iextrading.com/1.0"
    BATCH_LIMIT_IEX = 100

    # JSON data parsing methods
    def _parse_quote(symbol, data):
        #pprint(data)
        quote = data[cdt.QUOTE.value]
        #pprint(quote)
        series = pd.Series(quote)
        #print(series)
        print("quote")
        return series

    def _parse_earnings(symbol, data):
        pass

    def _parse_financials(symbol, data):
        print("financials")
        intermediate = data[cdt.FINANCIALS.value]
        if not intermediate:
            return None
        financials = intermediate[cdt.FINANCIALS.value]
        #print(intermediate)
        #pprint(financials)
        series = pd.DataFrame(financials)

        #print(series)
        return series

    MARKET_DATA_TYPES = [(cdt.QUOTE.value, _parse_quote),
                         (cdt.EARNINGS.value, _parse_earnings),
                         (cdt.FINANCIALS.value, _parse_financials),
                         (cdt.KEY_STATS.value, _parse_stats),
                         (cdt.COMPANY.value, _parse_company),
                        ]

    def __init__(self):
        self.cache = Cache()
        self.data_manager = DataManager(self.cache)
        self.market_data = self._read_market_data()

    def _read_market_data(self):
        earnings = self.cache.read(cdt.EARNINGS)
        if earnings is None:
            self._api_request_market_data()

    def cache_refresh(self):
        self.market_data = _api_request_market_data()

    def company_info(self, symbol):
        http_req = "/" + cdt.STOCK.value + "/" + symbol + "/" + cdt.COMPANY.value
        response = requests.get(self.API_URL_IEX + http_req)
        json = response.json()
        df = json_normalize(json)
        pprint(json)
        print(df)

    def _api_request_time_series(self, symbols, range):
        dfs = []
        for symbol in symbols:
            request_base = ("/" + cdt.STOCK.value + "/" + symbol + "/" +
                            cdt.CHART.value + "/" + range)
            response = requests.get(url=self.API_URL_IEX + request_base)
            series_list = [pd.Series(day) for day in response.json()]
            df = pd.concat(series_list, axis=1).transpose()
            dfs.append(df)
        return dfs

    def _api_request_market_data(self):
        symbol_batches = list(Utils.chunks(self.symbols, self.BATCH_LIMIT_IEX))
        request_base = ("/" + cdt.STOCK.value + "/" + cdt.MARKET.value + "/" +
                        cdt.BATCH.value + "?")
        print("Requesting market data through API...")
        datatypes = ",".join([i[0] for i in self.MARKET_DATA_TYPES])
        for batch in symbol_batches:
            #set up the parameters for API request
            params = dict(
                symbols = ','.join(batch),
                types = datatypes
            )
            #this JSON object will make a fine addition to my collection
            response_json = requests.get(url=self.API_URL_IEX + request_base, params=params).json()
            for symbol, data in response_json.items():
                self.earnings_manager.add_symbol(symbol, data)
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
