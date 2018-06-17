from alphavantage import AlphaVantage
#from iex_trading import IEXTrading
from pprint import pprint
import requests
import csv
from cache.cache import Cache
from data.data_manager import DataManager

AV_API_KEY = "7NMFQZSBM2Y5BJV6"

class Profit(object):
    def __init__(self):
        self.data_manager = DataManager()
        self.data_manager.data_refresh()

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
