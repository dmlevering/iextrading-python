from alphavantage import AlphaVantage
from iex_trading import IEXTrading
from stock import Stock

AV_API_KEY = "7NMFQZSBM2Y5BJV6"

class Profit:
    def __init__(self):
        av = AlphaVantage(AV_API_KEY)
        iex = IEXTrading()

def main():
    profit = Profit()

if __name__ == "__main__":
    main()
