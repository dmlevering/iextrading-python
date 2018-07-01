from json_parser import JsonParser
from datatype import DataType
from multiprocessing.pool import ThreadPool
from pprint import pprint
import requests

class TimeSeries(object):
    """
    This class handles gathering time series data for specific stocks
    from the IEX Trading API v1.0
    """

    #constants
    THREAD_COUNT    = 5
    BATCH_LIMIT_IEX = 100
    API_URL_IEX     = "https://api.iextrading.com/1.0"
    VALID_RANGES    = [
        "5y",      #historically adjusted market-wide data
        "2y",      #^
        "ytd",     #^
        "6m",      #^
        "3m",      #^
        "1m",      #^
        "1d",      #IEX-only data by minute
        "date",    #IEX-only data by minute for a specified date
                   #in the format YYYYMMDD (e.g., /date/19970408)
        "dynamic", #returns 1d or 1m data depending on the day
                   #or week and time of day. Intraday per minute
                   #data is only returned during market hours.
    ]

    def __init__(self, cache):
        self.cache = cache
        self.datatype = DataType("chart", "chart.csv")

    def get_time_series(self, symbols, range):
        if range not in self.VALID_RANGES:
            print("Error - invalid range: " + range)
            return None

        symbol_batches = list(self._splits(symbols, self.BATCH_LIMIT_IEX))
        print("Requesting time series data through IEX Trading API...")

        #parallelize API requests with a thread pool
        pool = ThreadPool(self.THREAD_COUNT)
        json_list = pool.starmap(self._api_request_time_series,
                                 zip(symbol_batches, [range] * len(symbol_batches)))
        pool.close()
        pool.join()

        #combine json responses
        json_data = {}
        for json_response in json_list:
            json_data.update(json_response)

        pprint(json_data)

        df = JsonParser.parse_hier2(json_data, "chart")
        self.cache.write(self.datatype, df)

    def _api_request_time_series(self, batch, range):
        request_base = "/stock/market/batch?"

        #set up the parameters for API request
        params = dict(
            symbols = ",".join(batch),
            types = "chart",
            range = range
        )
        #this response will make a fine addition to my collection
        response_json = requests.get(url=self.API_URL_IEX + request_base, params=params).json()
        return response_json

    def _splits(self, l, n):
        #yield successive n-sized splits from list l
        for i in range(0, len(l), n):
            yield l[i:i + n]
