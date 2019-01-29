import csv
import pickle
from datetime import datetime, timedelta
import pandas as pd

class DataType(object):
    """
    IEX Trading API data type. Barebones right now but will likely be expanded
    in the future.
    """
    def __init__(self, name):
        self.name = name
        self.csv_filename = name + ".csv"

    def get_csv_filename(self):
        return self.csv_filename

    def get_name(self):
        return self.name

class DataStore(object):
    """
    A database/cache of sorts for individual data types. Each DataStore contains the following:
        1. A DataType
        2. A parsing function (input: JSON data from API, output: Pandas DataFrame)
        3. A Pandas DataFrame (None if no data exists)
        4. A metadata filename; for now, file stores the timestamp this data was last refreshed
        5. A CSV filename; file stores the actual market data, refreshed when appropriate
        6. A datetime object representing the last time this data was updated (None if never)
    """

    MAX_DATA_AGE = 120
    PATH_CACHE = "cache/"
    PATH_META = "meta/"

    def __init__(self, name, parser):
        self.datatype = DataType(name)
        self.parser = parser
        self.df = None
        self.metadata_path = self.PATH_CACHE + self.PATH_META + "meta_" + name + ".pkl"
        self.csv_path = self.PATH_CACHE + self.datatype.get_csv_filename()
        self.datetime = None

        #attempt to load from drive
        self.df = self.load_from_drive()
        if self.df is not None:
            print("'" + name + "' DataFrame loaded successfully from drive.")
        else:
            print("'" + name + "' data could not be loaded from drive.")

    def is_data_fresh(self, timestamp):
        if timestamp is None:
            return False
        max_age = datetime.now() - (datetime.now() - timedelta(minutes=self.MAX_DATA_AGE))
        data_age = datetime.now() - timestamp
        return data_age < max_age

    def read_csv(self, path):
        df = pd.read_csv(self.csv_path)
        if df is not None:
            return df
        print("Failed to read DataFrame from CSV...")
        return None

    #return fresh Pandas DataFrame or None if data is stale/nonexistant
    def load_from_drive(self):
        try:
            #attempt to open metadata file
            with open(self.metadata_path, 'rb') as f_meta:
                #load timestamp from metadata file
                self.datetime = pickle.load(f_meta)
                if self.is_data_fresh(self.datetime):
                    #data is fresh; return Pandas DataFrame from CSV file
                    print("Fresh data! Reading cached '" + self.datatype.get_name() + "' data...", end=' ')
                    return self.read_csv(self.csv_path)
                else:
                    #data is stale or nonexistant; return None
                    return None

        except OSError as err:
            #it's likely that the metadata file hasn't been created yet
            print("Caught OSError: {0}".format(err))
            return None

    def parse_and_save(self, json_data):
        #if data is already fresh, don't bother parsing/saving
        if self.is_data_fresh(self.datetime):
            return

        #parse JSON data into Pandas DataFrame
        self.df = self.parser(json_data, self.datatype.get_name())

        #save Pandas DataFrame as CSV
        self.df.to_csv(self.csv_path)

        #update timestamp in metadata file
        with open(self.metadata_path, 'wb+') as f:
            pickle.dump(datetime.now(), f, pickle.HIGHEST_PROTOCOL)

    def get_name(self):
        return self.datatype.get_name()

    def get_df(self):
        return self.df

    def get_datatype(self):
        return self.datatype
