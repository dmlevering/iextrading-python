from alphavantage import AlphaVantage
from iex_trading import IEXTrading
from stock import Stock
from bs4 import BeautifulSoup
from pprint import pprint
import requests
import csv

AV_API_KEY = "7NMFQZSBM2Y5BJV6"

class Profit(object):
    def __init__(self):
        self.av = AlphaVantage(AV_API_KEY)
        self.iex = IEXTrading()
        self.sp500 = self.get_sp500()
        symbols = self.read_symbols()
        #self.iex.refresh(symbols)
        #self.iex.company_info("AAPL")
        self.av.time_series("AAPL")

    def get_sp500(self):
        #grab the list of S&P 500 symbols (tickers) from Wikipedia
        response = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        soup = BeautifulSoup(response.text, 'lxml')
        table = soup.find('table', {'class': 'wikitable sortable'})
        symbols = []
        for row in table.findAll('tr')[1:]:
            symbol = row.findAll('td')[0].text
            symbols.append(symbol)
        return sorted(symbols)

    def read_symbols(self):
        symbols = set()
        with open("symbols/nasdaq.csv") as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                symbols.add(row[0])
        with open("symbols/nyse.csv") as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                symbols.add(row[0])
        with open("symbols/amex.csv") as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                symbols.add(row[0])
        return sorted(list(symbols))

    def get_nasdaq(self):
        with open("symbols/NASDAQ.csv") as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                print(row[0])



def main():
    profit = Profit()



if __name__ == "__main__":
    main()
