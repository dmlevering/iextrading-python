from flask import Flask, render_template
import cufflinks as cf

from market import Market
from time_series import TimeSeries
from cache import Cache
from plot import Plot

app = Flask(__name__)
app.debug = True
app._static_folder = ""

@app.route('/')
def index():
    cache = Cache()
    market = Market(cache)
    ts = TimeSeries(cache)
    #market.data_refresh()
    df = ts.get_time_series(["GOOG", "AMZN"], "2y") #"MSFT", "AMD", "NVDA"
    plots_json = Plot.plot_time_series(df)

    # Render the Template
    return render_template("index.html", plot_json=plots_json)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
