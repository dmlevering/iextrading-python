import requests

class AlphaVantage:
    AV_API_URL = "http://www.alphavantage.co/query?"

    def __init__(self, api_key=None):
        if api_key is None:
            raise ValueError("Please supply an AlphaVantage API key. "
                             "They're free at https://www.alphavantage.co/support/#api-key")
        self.key = api_key

    def _api_call(self, params):
        response = requests.get(url=AV_API_URL, params=params)
        json_response = response.json()
        if "Error Message" in json_response:
            raise ValueError(json_response["Error Message"])
        return json_response
    


#import requests

#use python3!

# #base url for AlphaVantage API
# url = "https://www.alphavantage.co/query?"
#
# #set up the parameters for our API request
# params = dict(
#     #API's (required) parameters:
#     #API key
#     apikey = "7NMFQZSBM2Y5BJV6",
#     #the time series of your choice
#     function = "TIME_SERIES_INTRADAY",
#     #the name of the equity of your choice
#     symbol = "MSFT",
#     #time interval between two consecutive data points in the time series
#     interval = "1min",
#
#     #API's (optional) parameters:
#     #format specifier (JSON)
#     datatype = "json",
#     #ouput size: "full" returns the full-length time series
#     outputsize = "full"
# )
#
# #send a GET request to AlphaVantage and grab the JSON data
# response = requests.get(url=url, params=params)
# data = response.json()
#
# #'data' contains metadata and actual market data
# print(data["Meta Data"])
# symbol = data["Meta Data"]["2. Symbol"]
# market_data = data["Time Series (1min)"]
# for time, info in market_data.items():
#     print(symbol + " @ " + time + ": [opening_price: " + info["1. open"] +
#             ", closing_price:" + info["4. close"] + "]")
