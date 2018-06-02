import requests

class IEXTrading:
    IEX_API_URL = "https://api.iextrading.com/1.0"

    def __init__(self):
        print("IEX!")

    def api_call(self, params):
        response = requests.get(url=IEX_API_URL, params=params)
        json_response = response.json()
        return json_response
