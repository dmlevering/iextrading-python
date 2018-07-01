from json_parser import JsonParser
from datatype import DataType
from multiprocessing import Process
from multiprocessing.dummy import Pool
import csv
import requests
from pprint import pprint

class Market(object):
    """
    This class handles gathering general market data from the IEX Trading API v1.0
    """
    #constants
    PATH_SYMBOLS    = "symbols/"
    FILENAME_NASDAQ = "nasdaq.csv"
    FILENAME_NYSE   = "nyse.csv"
    FILENAME_AMEX   = "amex.csv"

    BATCH_LIMIT_IEX = 100
    API_URL_IEX     = "https://api.iextrading.com/1.0"
    THREAD_COUNT    = 30

    def __init__(self, cache):
        self.cache = cache
        self.symbols = self._read_symbols()
        self.json_data = None

        #datastores
        self.earnings_data   = DataStore("earnings",   JsonParser.parse_hier1)
        self.quote_data      = DataStore("quote",      JsonParser.parse_flat )
        self.financials_data = DataStore("financials", JsonParser.parse_hier1)
        self.stats_data      = DataStore("stats",      JsonParser.parse_flat )
        self.company_data    = DataStore("company",    JsonParser.parse_flat )

        self.datastores = [
            self.earnings_data,
            self.quote_data,
            self.financials_data,
            self.stats_data,
            self.company_data,
        ]

    def data_refresh(self):
        symbol_batches = list(self._splits(self.symbols, self.BATCH_LIMIT_IEX))
        print("Requesting market data through IEX Trading API...")

        #parallelize API requests with a thread pool. Python threads are a reasonable
        #choice here because the bottleneck is network latency, not processing power.
        pool = Pool(self.THREAD_COUNT)
        json_list = pool.map(self._api_request, symbol_batches)
        pool.close()
        pool.join()

        #combine json responses
        self.json_data = {}
        for json_response in json_list:
            self.json_data.update(json_response)

        #parallelize parsing with a process for each data type.
        #Use processes instead of threads because python's threads often don't take
        #advantage of multiple cores.
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
        #this response will make a fine addition to my collection
        response_json = requests.get(url=self.API_URL_IEX + request_base, params=params).json()
        return response_json

    def _read_symbols(self):
        """
        Read a list of symbols (tickers) into memory
        """
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

    def _splits(self, l, n):
        #yield successive n-sized splits from list l
        for i in range(0, len(l), n):
            yield l[i:i + n]

class DataStore(object):
    """
    Stores a Pandas DataFrame and the relevant parsing function for this
    datatype
    """
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
