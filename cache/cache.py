import pickle
from constants import Constants

class Cache(object):
    MAX_DATA_AGE = 120
    PATH_CACHE = "cache/"
    FILENAME_METADATA = "meta.data"

    def __init__(self):
        pass

    def write(self, lock, datatype, df):
        lock.acquire()
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
            lock.release()

    def read(self, lock, datatype):
        lock.acquire()
        try:
            #return value
            ret = None

            #determine paths
            path_meta = self.PATH_CACHE + self.FILENAME_METADATA

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
            lock.release()
            return ret

    def _metadata_read(self):
        #should already hold the lock
        #determine paths
        path_meta = self.PATH_CACHE + self.FILENAME_METADATA

        #attempt to load existing metadata
        try:
            with open(path_meta, 'rb') as f_meta:
                return pickle.load(f_meta)
        except OSError as err:
            #it's likely that the metadata file hasn't been created yet
            print("Caught OSError: {0}".format(err))
            return None

    def _metadata_write(self, metadata, datatype):
        #should already hold the lock
        #determine paths
        path_meta = self.PATH_CACHE + self.FILENAME_METADATA

        metadata.set_datetime(datatype)
        with open(path_meta, 'wb+') as f:
            pickle.dump(metadata, f, pickle.HIGHEST_PROTOCOL)

    def _get_path(self, datatype):
        return self.PATH_CACHE + datatype + ".csv"

class Meta(object):
    def __init__(self):
        self.datetime_earnings = None

    def set_datetime(self, datatype):
        if datatype == Constants.DataType.EARNINGS:
            self.datetime_earnings = datetime.now()

    def get_datetime(self, datatype):
        if datatype == Constants.DataType.EARNINGS:
            return self.datetime_earnings
