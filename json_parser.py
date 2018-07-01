import pandas as pd

class JsonParser(object):
    """
    Static helper class for parsing JSON objects into Pandas DataFrames

    json_data's structure for batch requests:
    {
      symbol1 : {
                  flat_data  : {
                                 key1 : value,
                                 key2 : value,
                               },
                  hier_data1 : {
                                 key1 : value,
                                 key2 : [
                                          {
                                            key3 : value,
                                            key4 : value,
                                          },
                                          {
                                            key3 : value,
                                            key4 : value,
                                          },
                                        ],
                               },
                },
      symbol2 : {
                  flat_data  : {
                                 key1 : value,
                                 key2 : value,
                               },
                  hier_data2 : [
                                 {
                                   key1 : value,
                                   key2 : value,
                                 },
                                 {
                                   key1 : value,
                                   key2 : value,
                                 },
                               ],
                },
    }
    """

    def parse_flat(json_data, datatype_name):
        """
        datatype_name has flat_data structure
        """
        intermediate_list = []
        for symbol, datatypes in json_data.items():
            data = datatypes[datatype_name]
            series = pd.Series(data)
            intermediate_list.append(series)
        df = pd.concat(intermediate_list, axis=1, sort=True).transpose()
        df.set_index("symbol", inplace=True)
        return df

    def parse_hier1(json_data, datatype_name):
        """
        datatype_name has hier_data1 structure
        """
        intermediate_list = []
        for symbol, datatypes in json_data.items():
            data = datatypes[datatype_name]
            if not data:
                continue
            rows = data[datatype_name]

            #build MultiIndex
            indices = [(symbol, "-"+str(i+1)+"q") for i in range(len(rows))]
            hier_index = pd.MultiIndex.from_tuples(indices)
            df = pd.DataFrame(rows, hier_index)
            intermediate_list.append(df)
            #print(df)
        return pd.concat(intermediate_list, sort=True)

    def parse_hier2(json_data, datatype_name):
        """
        datatype_name has hier_data2 structure
        """
        intermediate_list = []
        for symbol, datatypes in json_data.items():
            data = datatypes[datatype_name]

            #build MultiIndex
            indices = [(symbol, i) for i in range(len(data))]
            hier_index = pd.MultiIndex.from_tuples(indices)
            df = pd.DataFrame(data, hier_index)
            intermediate_list.append(df)
            #print(df)
        return pd.concat(intermediate_list, sort=True)
