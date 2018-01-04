import numpy as np
from utils import histo_plotter

class LineHeightCalculator(object):

    def __init__(self):
        self.yes = "yes"

    def calculate_line_height_ocropus(self, lines_input):

        PRINT_OUTPUT = True
        FILTER_NEGATIVE_VALUE = True  # sometimes overlapping lines produce negative line gaps
        DO_ANALYSIS_STUFF = False

        y_gaps = []

        for line_index, line in enumerate(lines_input):
            previous_line_index = line_index -1
            previous_line = ""
            if previous_line_index >= 0:
                previous_line = lines_input[previous_line_index]
            else:
                continue

            (xp_start, yp_start, xp_end, yp_end) = previous_line.coordinates  # 'p' for previous
            (xc_start, yc_start, xc_end, yc_end) = line.coordinates           # 'c' for current

            y_gap = yc_start - yp_end

            if FILTER_NEGATIVE_VALUE is True:
                if y_gap >= 0:
                    y_gaps.append(y_gap)
                    if PRINT_OUTPUT is True:
                        print("Index:", line_index, "Gap:", y_gap)
            else:
                y_gaps.append(y_gap)
                if PRINT_OUTPUT is True:
                    print("Index:", line_index, "Gap:", y_gap)

        # generate borders for histogram segments
        bins = self.generate_bins(0, 3, 33)

        hist, bin_edges = np.histogram(y_gaps, bins)
        edge_max = self.get_max_hist_edge(hist, bin_edges)

        if DO_ANALYSIS_STUFF is True:
            # further methods and plots for comparison and analysis of best result

            # plot base histogram
            hp = histo_plotter.HistogramPlotter()
            hp.plot_histogram(y_gaps, bins)
            hp.plot_histogram_equally(y_gaps)

            histA, bin_edgesA = np.histogram(y_gaps, bins='auto')
            edge_maxA = self.get_max_hist_edge(histA, bin_edgesA)

            histSqrt, bin_edgesSqrt = np.histogram(y_gaps, bins='sqrt')
            edge_maxSqrt = self.get_max_hist_edge(histSqrt, bin_edgesSqrt)

        # return the detected line height
        return edge_max

    def generate_bins(self, start_value=0, increment=5, bin_count=20):

        PRINT_OUTPUT = False

        bins = []
        bin_increment = increment
        bin_current_number = start_value

        for index in range(0,bin_count):
            bins.append(bin_current_number)
            bin_current_number += bin_increment

        if PRINT_OUTPUT is True:
            print("Bins:", bins)

        return bins

    def get_max_hist_edge(self, hist, bin_edges):

        PRINT_OUTPUT = False

        bin_max = np.where(hist == hist.max())
        detected_edges = bin_edges[bin_max]
        detected_edge = detected_edges[0]

        if PRINT_OUTPUT is True:
            print('maxbin', detected_edge)

        return detected_edge

