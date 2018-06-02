from iex_trading import IEXTrading

class Stock:
    def __init__(self, symbol):
        self.symbol = symbol

        #request info about this company (name, exchange, issue type, etc)
        iex = IEXTrading()
        company_info = iex.company_info(symbol)
