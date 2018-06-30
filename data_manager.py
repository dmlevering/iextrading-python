from json_parser import JsonParser
from multiprocessing import Process
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

    def __init__(self):
        self.cache = Cache()
        self.symbols = self._read_symbols()
        self.json_data = None

        #datastores
        self.earnings_data = EarningsData()
        self.quote_data = QuoteData()
        self.financials_data = FinancialsData()
        self.stats_data = StatsData()
        self.company_data = CompanyData()

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

    def _api_request(self, datatypes):
        pass

    def data_refresh(self):
        datatypes = ",".join([d.get_datatype().get_name() for d in self.datastores])
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
            #strange syntax for concatenating two dictionaries (probably slow)
            json_collection = {**json_collection, **response_json}
        self.json_data = json_collection

        #parallelize by parsing each datatype in a separate process.
        #Use processes instead of threads because python's threads do not take
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

    def splits(self, l, n):
        #yield successive n-sized splits from list l
        for i in range(0, len(l), n):
            yield l[i:i + n]

class CompanyData(object):
    def __init__(self):
        self.df = None
        self.name = "company"
        self.datatype = DataType(self.name, self.name + ".csv")

    def get_name(self):
        return self.name

    def get_df(self):
        return self.df

    def get_datatype(self):
        return self.datatype

    def refresh(self, json_data, cache):
        self.df = JsonParser.parse_flat(json_data, self.datatype.get_name())
        cache.write(self.datatype, self.df)

class QuoteData(object):
    def __init__(self):
        self.df = None
        self.name = "quote"
        self.datatype = DataType(self.name, self.name + ".csv")

    def get_name(self):
        return self.name

    def get_df(self):
        return self.df

    def get_datatype(self):
        return self.datatype

    def refresh(self, json_data, cache):
        self.df = JsonParser.parse_flat(json_data, self.datatype.get_name())
        cache.write(self.datatype, self.df)

class StatsData(object):
    def __init__(self):
        self.df = None
        self.name = "stats"
        self.datatype = DataType(self.name, self.name + ".csv")

    def get_name(self):
        return self.name

    def get_df(self):
        return self.df

    def get_datatype(self):
        return self.datatype

    def refresh(self, json_data, cache):
        self.df = JsonParser.parse_flat(json_data, self.datatype.get_name())
        cache.write(self.datatype, self.df)

class EarningsData(object):
    def __init__(self):
        self.df = None
        self.name = "earnings"
        self.datatype = DataType(self.name, self.name + ".csv")

    def get_name(self):
        return self.name

    def get_df(self):
        return self.df

    def get_datatype(self):
        return self.datatype

    def refresh(self, json_data, cache):
        self.df = JsonParser.parse_hier(json_data, self.datatype.get_name())
        cache.write(self.datatype, self.df)

class FinancialsData(object):
    def __init__(self):
        self.df = None
        self.name = "financials"
        self.datatype = DataType(self.name, self.name + ".csv")

    def get_name(self):
        return self.name

    def get_df(self):
        return self.df

    def get_datatype(self):
        return self.datatype

    def refresh(self, json_data, cache):
        self.df = JsonParser.parse_hier(json_data, self.datatype.get_name())
        cache.write(self.datatype, self.df)
