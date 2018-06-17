from data.earnings_manager import EarningsManager
from multiprocessing import Process, Lock
import csv
import requests
from pprint import pprint

class DataManager(object):
    #constants
    PATH_SYMBOLS    = "symbols/"
    FILENAME_NASDAQ = "nasdaq.csv"
    FILENAME_NYSE   = "nyse.csv"
    FILENAME_AMEX   = "amex.csv"

    BATCH_LIMIT_IEX = 100
    API_URL_IEX     = "https://api.iextrading.com/1.0"

    def __init__(self, cache):
        self.cache = cache
        self.symbols = self._read_symbols()

        #data managers
        self.earnings_manager = EarningsManager(self.cache)

        self.managers = [
            self.earnings_manager,
        ]

    def _read_symbols(self):
        #read a list of symbols (tickers)
        symbols = set()
        with open(self.PATH_SYMBOLS + self.FILENAME_NASDAQ, "r") as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                symbols.add(row[0])
        with open(self.PATH_SYMBOLS + self.FILENAME_NYSE, "r") as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                symbols.add(row[0])
        with open(self.PATH_SYMBOLS + self.FILENAME_AMEX, "r") as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                symbols.add(row[0])
        return sorted(list(symbols))

    def data_refresh(self):
        datatypes = ",".join([m.get_datatype() for m in self.managers])
        symbol_batches = list(self.splits(self.symbols, self.BATCH_LIMIT_IEX))
        request_base = "/stock/market/batch?"
        print("Requesting market data through API...")
        json_collection = {}
        for batch in symbol_batches:
            #set up the parameters for API request
            params = dict(
                symbols = ",".join(batch),
                types = datatypes
            )
            #this JSON object will make a fine addition to my collection
            response_json = requests.get(url=self.API_URL_IEX + request_base, params=params).json()
            #strange syntax for concatenating two dictionaries
            json_collection = {**json_collection, **response_json}

        #parallelize the parsing through separate processes (python's threading is... fake)
        processes = []
        lock = Lock()
        for manager in self.managers:
            process = Process(target=manager.refresh, args=(lock, json_collection))
            process.start()
            processes.append(process)

        #wait for all processes to complete before proceeding
        for process in processes:
            process.join()

    def splits(self, l, n):
        #yield successive n-sized splits from list l
        for i in range(0, len(l), n):
            yield l[i:i + n]
