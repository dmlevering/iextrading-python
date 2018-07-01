from flask import Flask, render_template
import cufflinks as cf

from market import Market
from time_series import TimeSeries
from cache import Cache
from plot import Plot

import json
import plotly

import pandas as pd
import numpy as np
import plotly.graph_objs as go

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    cache = Cache()
    market = Market(cache)
    time_series = TimeSeries(cache)
    #self.market.data_refresh()
    df = time_series.get_time_series(["GOOG", "AMZN"], "ytd") #"MSFT", "AMD", "NVDA"
    graph = df[["date", "close"]]
    graph = graph.reset_index(level=1, drop=True)
    #graph = graph.unstack()
    print(graph)
    #df2 = df.loc["GOOG", :]
    graph["date"] = pd.to_datetime(graph["date"])
    #df2.set_index("date", inplace=True)
    #Plot.plot(graph, "Stock Price Over Time")

    labels, plots = [], []
    for label, group in graph.groupby(graph.index):
        labels.append(label)
        scatter = go.Scatter(x=group["date"], y=group["close"], name=label, mode="lines")
        plots.append(scatter)

    # Create the Plotly Data Structure
    graph2 = dict(
        data= plots,
        layout=dict(
            title='Bar Plot',
            yaxis=dict(
                title="Count"
            ),
            xaxis=dict(
                title="Fruit"
            )
        )
    )

    # Convert the figures to JSON
    graphJSON = json.dumps(graph2, cls=plotly.utils.PlotlyJSONEncoder)

    # Render the Template
    return render_template('layouts/index.html', graphJSON=graphJSON)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999)
