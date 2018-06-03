import requests
from pprint import pprint
from utils import Utils
from stock import Stock
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize

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
        json = response.json()
        df = json_normalize(json)
        pprint(json)
        print(df)

    def refresh(self, symbols):
        batches = list(Utils.chunks(symbols, 100))
        base = "/stock/market/batch?"
        print("Gathering market data...")
        series = []
        count = 0
        for chunk in batches:
            #set up the parameters for our API request
            params = dict(
                symbols = ','.join(chunk),
                types = "quote" #price,ohlc,stats,
            )
            response = requests.get(url=IEX_API_URL + base, params=params)
            json = response.json()
            for k,v in json.items():
                for qk, val in v.items():
                    ser = pd.Series(val)
                    series.append(ser)
            count += 1
            if count == 4:
                break
        df = pd.concat(series, axis=1)
        print(df.transpose())
        print("Done!")
