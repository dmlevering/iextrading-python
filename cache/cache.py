import pickle
from constants import Constants

class Cache(object):
    MAX_DATA_AGE = 120
    FILENAME_METADATA = "meta.data"

    def __init__(self):
        pass

    def write(self, datatype, df):
        #save data
        path_data = self.get_path(datatype)
        df.to_csv(path_data)

        #attempt to load existing metadata
        metadata = self._metadata_read()
        if metadata is None:
            metadata = Meta()

        #save metadata
        self._metadata_write(metadata, datatype)

    def read(self, datatype):
        #determine paths
        path_meta = self.FILENAME_METADATA

        #attempt to load existing metadata
        metadata = self._metadata_read()
        if metadata is None:
            return None

        #is data fresh?
        max_age = datetime.now() - (datetime.now() - timedelta(minutes=self.MAX_DATA_AGE))
        data_age = datetime.now() - metadata.get_datetime(datatype)
        if data_age > max_age:
            #stale data...
            print("Stale data...")
            return None
        else:
            #fresh data!
            print("Fresh data...\nReading cached " + datatype.value + " data...")
            return pd.read_csv(path_meta)

    def _metadata_read(self):
        #determine paths
        path_meta = self.FILENAME_METADATA

        #attempt to load existing metadata
        try:
            with open(self.FILENAME_METADATA, 'rb') as f_meta:
                return pickle.load(f_meta)
        except OSError as err:
            #it's likely that the metadata file hasn't been created yet
            print("Caught OSError: {0}".format(err))
            return None

    def _metadata_write(self, metadata, datatype):
        metadata.set_datetime(datatype)
        with open(path_meta, 'wb+') as f:
            pickle.dump(metadata, f, pickle.HIGHEST_PROTOCOL)

class Meta(object):
    def __init__(self):
        self.datetime_earnings = None

    def set_datetime(self, datatype):
        if datatype == Constants.DataType.EARNINGS:
            self.datetime_earnings = datetime.now()

    def get_datetime(self, datatype):
        if datatype == Constants.DataType.EARNINGS:
            return self.datetime_earnings
