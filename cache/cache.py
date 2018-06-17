import pickle
from data.datatype import DataType
from datetime import datetime, timedelta

class Cache(object):
    MAX_DATA_AGE = 120
    PATH_CACHE = "cache/"
    FILENAME_METADATA = "meta.data"

    def __init__(self, lock):
        self.lock = lock
        self.meta_path = self.PATH_CACHE + self.FILENAME_METADATA

    def add_manager(self, manager):
        pass

    def write(self, datatype, df):
        self.lock.acquire()
        try:
            #save data
            path_data = self._get_path(datatype)
            df.to_csv(path_data)

            #attempt to load existing metadata
            metadata = self._metadata_read()
            if metadata is None:
                metadata = Meta()

            #save metadata
            self._metadata_write(metadata, datatype)
        finally:
            self.lock.release()

    def read(self, datatype):
        self.lock.acquire()
        try:
            #return value
            ret = None

            #attempt to load existing metadata
            metadata = self._metadata_read()
            if metadata is None:
                raise Exception("No metadata file exists!")

            #is data fresh?
            max_age = datetime.now() - (datetime.now() - timedelta(minutes=self.MAX_DATA_AGE))
            data_age = datetime.now() - metadata.get_datetime(datatype)
            if data_age > max_age:
                #stale data...
                raise Exception("Stale data...")
            else:
                #fresh data!
                print("Fresh data...\nReading cached " + datatype.value + " data...")
                ret = pd.read_csv(path_meta)
        except Exception as e:
            print(e.args)
            ret = None
        finally:
            self.lock.release()
            return ret

    def _metadata_read(self):
        #should already hold the lock
        #attempt to load existing metadata
        try:
            with open(self.meta_path, 'rb') as f_meta:
                return pickle.load(f_meta)
        except OSError as err:
            #it's likely that the metadata file hasn't been created yet
            print("Caught OSError: {0}".format(err))
            return None

    def _metadata_write(self, metadata, datatype):
        #should already hold the lock
        metadata.set_datetime(datatype)
        with open(self.meta_path, 'wb+') as f:
            pickle.dump(metadata, f, pickle.HIGHEST_PROTOCOL)

    def _get_path(self, datatype):
        return self.PATH_CACHE + datatype.get_filename()

#this class should never be accessed without holding the Cache lock
class Meta(object):

    def __init__(self):
        self.datetime_earnings = None
        self.datetime_quote = None

    def get_path(self):
        return self.path

    def set_datetime(self, datatype):
        if datatype.get_name() == "earnings": #TODO: fix this
            self.datetime_earnings = datetime.now()
        elif datatype.get_name() == "quote":
            self.datetime_quote = datetime.now()

    def get_datetime(self, datatype):
        if datatype.get_name() == "earnings": #TODO: fix this
            return self.datetime_earnings
        elif datatype.get_name() == "quote":
            return self.datetime_quote
