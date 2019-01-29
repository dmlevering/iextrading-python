import matplotlib.pyplot as plt
import seaborn as sns
import json
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go
from pprint import pprint

class Plot(object):

    #constants
    SEABORN_STYLE_DARK = {
        "axes.axisbelow": True,
        "axes.edgecolor": "white",
        "axes.facecolor": "#020811",
        "axes.grid": True,
        "axes.labelcolor": ".15",
        "axes.linewidth": 0,
        "font.family": "Arial",
        "font.scale" : 1.2,
        "grid.color": "#1f2021",
        "grid.linestyle": "-",
        "image.cmap": "Greys",
        "legend.frameon": False,
        "legend.numpoints": 1,
        "legend.scatterpoints": 1,
        "lines.linewidth": 2,
        "lines.solid_capstyle": "round",
        "pdf.fonttype": 42,
        "text.color": "white",
        "xtick.color": ".15",
        "xtick.direction": "out",
        "xtick.major.size": 0,
        "xtick.minor.size": 0,
        "ytick.color": ".15",
        "ytick.direction": "out",
        "ytick.major.size": 0,
        "ytick.minor.size": 0
    }

    def plot_time_series(df, title="Time Series", xlabel="Date", ylabel="Close Price ($)",
                         x="date", y="close"):
        #create plots
        plots = []
        for label, group in df.groupby(df.index):
            scatter = go.Scatter(x=group[x], y=group[y], name=label, mode="lines")
            plots.append(scatter)

        return Plot.get_plotly_json(plots, title, xlabel, ylabel)

    def plot_marketcaps_over_time(df, market, title="Market Caps Over Time", xlabel="Date",
                                  ylabel="Share Price ($) * Shares Outstanding", x="date", y="close"):
        #create plots
        plots = []
        for label, group in df.groupby(df.index):
            shares_outstanding = market.stats_data.df.loc[market.stats_data.df['symbol'] == label]["sharesOutstanding"]
            scatter = go.Scatter(x=group[x], y=group[y] * int(shares_outstanding),
                                 name=label, mode="lines")
            plots.append(scatter)

        return Plot.get_plotly_json(plots, title, xlabel, ylabel)

    @staticmethod
    def plot(df, title, xlabel, ylabel, engine):
        if engine == "seaborn":
            #sns.set_context("notebook", font_scale=1.2, rc={})
            sns.set_style("dark", rc=Plot.SEABORN_STYLE_DARK)
            fig, ax = plt.subplots(figsize=(8,6))
            for label, group in df.groupby(df.index):
                group.plot(x="date", y="close", ax=ax, label=label)
            sns.despine()
            plt.title(title, color="black")
            plt.xlabel(xlabel, color="black")
            plt.ylabel(ylabel, color="black")
            plt.show()
        elif engine == "plotly":
            pass

    @staticmethod
    def get_plotly_json(plots, title, xlabel, ylabel):
        #create plotly JSON
        plotly_struct = dict(
            data = plots,
            layout = dict(
                title = title,
                xaxis = dict(
                    title = xlabel
                ),
                yaxis = dict(
                    title = ylabel
                )
            )
        )
        plots_json = json.dumps(plotly_struct, cls=plotly.utils.PlotlyJSONEncoder)
        return plots_json
