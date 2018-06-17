
class DataType(object):
    def __init__(self, name, filename, manager):
        self.name = name
        self.filename = filename
        self.manager = manager

    def get_filename(self):
        return self.filename

    def get_name(self):
        return self.name
