import pandas as pd
from pprint import pprint
class EarningsManager(object):
    def __init__(self, cache):
        self.cache = cache
        self.df = None
        self.datatype = "earnings"

    def get_df(self):
        return self.df

    def get_datatype(self):
        return self.datatype

    def refresh(self, lock, json_data):
        intermediate_list = []
        for symbol, data in json_data.items():
            intermediate = data[self.datatype]
            if not intermediate:
                continue
            earnings = intermediate[self.datatype]

            #build MultiIndex
            indices = [(symbol, "-"+str(i+1)+"q") for i in range(len(earnings))]
            hier_index = pd.MultiIndex.from_tuples(indices)
            df = pd.DataFrame(earnings, hier_index)
            intermediate_list.append(df)
            #print(df)
        self.df = pd.concat(intermediate_list, sort=True)
        self.cache.write(lock, self.datatype, self.df)
