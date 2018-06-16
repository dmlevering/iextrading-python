import pandas as pd
from constants import Constants
class EarningsManager(object):
    def __init__(self):
        self.df = None
        self.intermediate_list = []

    def get_df(self):
        return self.df

    def create_df(self):
        self.df = pd.concat(self.intermediate_list)
        print(self.df)

    def add_symbol(self, symbol, data):
        print("earnings")
        intermediate = data[Constants.DataType.EARNINGS.value]
        if not intermediate:
            return None
        earnings = intermediate[Constants.DataType.EARNINGS.value]

        #build MultiIndex
        indices = [(symbol, "-"+str(i+1)+"q") for i in range(len(earnings))]
        hier_index = pd.MultiIndex.from_tuples(indices)
        df = pd.DataFrame(earnings, hier_index)
        self.intermediate_list.append(df)
