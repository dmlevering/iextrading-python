from json_parser import JsonParser
from multiprocessing import Process
from multiprocessing.pool import ThreadPool
from cache import Cache
import csv
import requests
from pprint import pprint

class DataType(object):
    """
    IEX Trading API data type
    """
    def __init__(self, name, filename):
        self.name = name
        self.filename = filename

    def get_filename(self):
        return self.filename

    def get_name(self):
        return self.name

class DataManager(object):
    #constants
    PATH_SYMBOLS    = "symbols/"
    FILENAME_NASDAQ = "nasdaq.csv"
    FILENAME_NYSE   = "nyse.csv"
    FILENAME_AMEX   = "amex.csv"

    BATCH_LIMIT_IEX = 100
    API_URL_IEX     = "https://api.iextrading.com/1.0"
    THREAD_COUNT    = 15

    def __init__(self):
        self.cache = Cache()
        self.symbols = self._read_symbols()
        self.json_data = None

        #datastores
        self.earnings_data   = DataStore("earnings",   JsonParser.parse_hier)
        self.quote_data      = DataStore("quote",      JsonParser.parse_flat)
        self.financials_data = DataStore("financials", JsonParser.parse_hier)
        self.stats_data      = DataStore("stats",      JsonParser.parse_flat)
        self.company_data    = DataStore("company",    JsonParser.parse_flat)

        self.datastores = [
            self.earnings_data,
            self.quote_data,
            self.financials_data,
            self.stats_data,
            self.company_data,
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
        symbol_batches = list(self._splits(self.symbols, self.BATCH_LIMIT_IEX))
        print("Requesting market data through IEX Trading API...")

        #parallelize API requests with a thread pool
        thread_pool = ThreadPool(self.THREAD_COUNT)
        json_list = thread_pool.map(self._api_request, symbol_batches)
        json_collection = {}
        for json_dict in json_list:
            json_collection.update(json_dict)
        self.json_data = json_collection

        #parallelize parsing with a process for each data type
        #use processes instead of threads because python's threads don't take
        #advantage of multiple cores (they're meant for IO-bound functions)
        processes = []
        for datastore in self.datastores:
            process = Process(target=datastore.refresh,
                              args=(self.json_data, self.cache),
                              name=datastore.get_name())
            process.start()
            processes.append(process)
            print("Begin parsing " + process.name)

        #wait for all processes to complete before proceeding
        for process in processes:
            process.join()
            print("Finished parsing " + process.name)

    def _api_request(self, batch):
        request_base = "/stock/market/batch?"
        datatypes = ",".join([d.get_name() for d in self.datastores])
        #set up the parameters for API request
        params = dict(
            symbols = ",".join(batch),
            types = datatypes
        )
        #this JSON object will make a fine addition to my collection
        response_json = requests.get(url=self.API_URL_IEX + request_base, params=params).json()
        return response_json

    def _splits(self, l, n):
        #yield successive n-sized splits from list l
        for i in range(0, len(l), n):
            yield l[i:i + n]

class DataStore(object):
    def __init__(self, name, parser):
        self.df = None
        self.name = name
        self.datatype = DataType(self.name, self.name + ".csv")
        self.parser = parser

    def get_name(self):
        return self.name

    def get_df(self):
        return self.df

    def get_datatype(self):
        return self.datatype

    def refresh(self, json_data, cache):
        self.df = self.parser(json_data, self.datatype.get_name())
        cache.write(self.datatype, self.df)
