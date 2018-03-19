import matplotlib.pyplot as plt
import numpy as np


class HistogramPlotter(object):
    """
        Basic class for plotting histogram data with numpy
    """

    # def __init__(self):
        # self._example = "ASD"

    def plot_histogram(self, hist_input, bins_input):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.hist(hist_input, bins=bins_input, normed=True, fc='k', alpha=0.3)
        plt.show()

    def plot_histogram_equally(self, hist_input):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.hist(hist_input, bins=range(min(hist_input), max(hist_input), 1))
        plt.show()
