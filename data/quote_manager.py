import pandas as pd
from data.datatype import DataType
from pprint import pprint

class QuoteManager(object):
    def __init__(self, cache):
        self.cache = cache
        self.df = None
        self.datatype = DataType("quote", "quote.csv", self)

    def get_df(self):
        return self.df

    def get_datatype(self):
        return self.datatype

    def refresh(self, json_data):
        intermediate_list = []
        for symbol, data in json_data.items():
            quote = data[self.datatype.get_name()]
            series = pd.Series(quote)
            intermediate_list.append(series)
        self.df = pd.concat(intermediate_list, axis=1, sort=True).transpose()
        self.df.set_index("symbol", inplace=True)
        self.cache.write(self.datatype, self.df)
