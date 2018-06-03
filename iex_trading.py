import requests
from pprint import pprint
from utils import Utils

IEX_API_URL = "https://api.iextrading.com/1.0"
IEX_BATCH_LIMIT = 100

class IEXTrading:
    def __init__(self):
        pass

    def api_call(self, params):
        response = requests.get(url=IEX_API_URL, params=params)
        json_response = response.json()
        return json_response

    def company_info(self, symbol):
        http_req = "/stock/" + symbol + "/company"
        response = requests.get(IEX_API_URL + http_req)
        return response.json()

    def refresh(self, symbols):
        batches = list(Utils.chunks(symbols, 100))
        base = "/stock/market/batch?"
        for chunk in batches:
            #set up the parameters for our API request
            params = dict(
                symbols = ','.join(chunk),
                types = "price,ohlc,stats,quote"
            )
            response = requests.get(url=IEX_API_URL + base, params=params)
            data = response.json()
            pprint(data)
