import matplotlib.pyplot as plt
import seaborn as sns

class Plot(object):

    #constants
    STYLE_DARK = {
        "axes.axisbelow": True,
        "axes.edgecolor": "white",
        "axes.facecolor": "#020811",
        "axes.grid": True,
        "axes.labelcolor": ".15",
        "axes.linewidth": 0,
        "font.family": "Ariel",
        "grid.color": "#1f2021",
        "grid.linestyle": "-",
        "image.cmap": "Greys",
        "legend.frameon": False,
        "legend.numpoints": 1,
        "legend.scatterpoints": 1,
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

    def __init__(self):
        pass

    @staticmethod
    def plot(df, title):
        #sns.set_style("darkgrid")
        #sns.set_style("ticks")
        sns.set_context("notebook", font_scale=1.2, rc={"lines.linewidth": 2})
        #plt.rcParams.update(plt.rcParamsDefault)
        #plt.style.use("seaborn-paper")
        #sns.set()
        sns.set_style("dark", rc=Plot.STYLE_DARK)
        fig, ax = plt.subplots(figsize=(8,6))
        for label, group in df.groupby(df.index):
            group.plot(x="date", y="close", ax=ax, label=label)
        plt.legend()
        sns.despine()
        #df.groupby(df.index).plot(x="date", y="close", legend=True, ax=ax, label=df.index)
        #sns.plot()
        plt.title(title, color="black")
        plt.ylabel("Share price (dollars)")
        plt.xlabel("Date")
        #plt.tight_layout()
        plt.show()
