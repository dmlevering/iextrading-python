from alphavantage import AlphaVantage
from iex_trading import IEXTrading
from pprint import pprint
import requests
import csv

AV_API_KEY = "7NMFQZSBM2Y5BJV6"

class Profit(object):
    def __init__(self):
        self.av = AlphaVantage(AV_API_KEY)
        self.iex = IEXTrading()
        #symbols = self.read_symbols()
        #df = self.iex.refresh(symbols)
        #print(self.iex.best_peratio(df))
        #self.iex.company_info("AAPL")
        #self.av.time_series("AAPL")




def main():
    profit = Profit()



if __name__ == "__main__":
    main()
