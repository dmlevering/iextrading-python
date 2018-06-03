from iex_trading import IEXTrading
from pprint import pprint

class Stock:

    def __init__(self, symbol):
        self.symbol = symbol

        #request info about this company (name, exchange, issue type, etc)
        iex = IEXTrading()
        company_info = iex.company_info(symbol)
        pprint(company_info)
        self.company_name = company_info["companyName"]
        self.exchange = company_info["exchange"]
        self.industry = company_info["industry"]
        self.website = company_info["website"]
        self.description = company_info["description"]
        self.ceo = company_info["CEO"]
        self.issue_type = company_info["issueType"]
        self.sector = company_info["sector"]
