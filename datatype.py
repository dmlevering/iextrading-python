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
