from alphavantage import AlphaVantage
#from iex_trading import IEXTrading
from pprint import pprint
import requests
import csv
from market import Market
from time_series import TimeSeries
from cache import Cache
from plot import Plot
import pandas as pd

AV_API_KEY = "7NMFQZSBM2Y5BJV6"

class Profit(object):
    def __init__(self):
        self.cache = Cache()
        self.market = Market(self.cache)
        self.time_series = TimeSeries(self.cache)
        #self.market.data_refresh()
        df = self.time_series.get_time_series(["GOOG", "AMZN"], "ytd") #"MSFT", "AMD", "NVDA"
        graph = df[["date", "close"]]
        graph = graph.reset_index(level=1, drop=True)
        #graph = graph.unstack()
        print(graph)
        #df2 = df.loc["GOOG", :]
        graph["date"] = pd.to_datetime(graph["date"])
        #df2.set_index("date", inplace=True)
        Plot.plot(graph, "Stock Price Over Time")

        #self.av = AlphaVantage(AV_API_KEY)
        #self.iex = IEXTrading()
        #symbols = self.read_symbols()
        #df = self.iex.refresh(symbols)
        #print(self.iex.best_peratio(df))
        #self.iex.company_info("AAPL")
        #self.av.time_series("AAPL")





def main():
    profit = Profit()



if __name__ == "__main__":
    main()
