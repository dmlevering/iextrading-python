from flask import Flask, render_template
import sys

from market import Market
from time_series import TimeSeries
from plot import Plot
from pprint import pprint

app = Flask(__name__)
app.debug = True

def initialize():
    market = Market()
    market.get_most_active()
    market.get_gainers()
    market.get_losers()

    shares_outstanding = market.stats_data.df.loc[market.stats_data.df['symbol'] == "AMZN"]["sharesOutstanding"]
    print(type(int(shares_outstanding)), int(shares_outstanding))
    pprint(market.stats_data.df.loc[market.stats_data.df['symbol'] == "AMZN"]["sharesOutstanding"])

@app.route('/')
def index():
    market = Market()
    time_series = TimeSeries()
    df = time_series.get_time_series(["GOOG", "AMZN", "AAPL", "FB"], "2y") #"MSFT", "AMD", "NVDA"
    #plots_json = Plot.plot_time_series(df)
    plots_json = Plot.plot_marketcaps_over_time(df, market)

    #render index.html
    return render_template("index.html", plot_json=plots_json)

if __name__ == '__main__':
    #initialize market data
    if len(sys.argv) <= 1:
        initialize()

    #run flask app if user has specified -f or -flask
    if len(sys.argv) > 1:
        if sys.argv[1] == "-flask" or sys.argv[1] == "-f":
            app.run(host='127.0.0.1', port=5000)
