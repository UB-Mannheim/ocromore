import numpy as np
import statistics as stats
from utils import histo_plotter
from utils.random import Random
from utils.typecasts import TypeCasts
from my_hocr_parser.parser import HOCRDocument, Line, Paragraph, Area, Page


class LineHeightInformation(object):

    def __init__(self, line_distance, line_gap, line_height, len_line_gaps, len_line_heigths):
        self._line_distance = line_distance
        self._line_gap = line_gap
        self._line_height = line_height
        self._len_line_gaps = len_line_gaps
        self._len_line_heigths = len_line_heigths

    def set_textfield(self, text):
        self._info_field = text

    def get_line_distance(self):
        return self._line_distance

class LineHeightCalculator(object):

    def __init__(self):
        self.yes = "yes"

    def get_single_line_height(self, coordinates):
        (x_start, y_start, x_end, y_end) = coordinates
        line_height = y_end-y_start
        return line_height

    def calculate_line_distance_information(self, lines_input, do_analysis_stuff=False, return_class=False, info_field=None):

        PRINT_OUTPUT = True
        FILTER_NEGATIVE_VALUE = True  # sometimes overlapping lines produce negative line gaps

        y_gaps = []
        line_heights = []

        for line_index, line in enumerate(lines_input):
            previous_line_index = line_index -1
            previous_line = ""
            if previous_line_index >= 0:
                previous_line = lines_input[previous_line_index]
            else:
                lh = self.get_single_line_height(line.coordinates)
                if lh > 0:
                    line_heights.append(lh)
                continue

            (xp_start, yp_start, xp_end, yp_end) = previous_line.coordinates  # 'p' for previous
            (xc_start, yc_start, xc_end, yc_end) = line.coordinates           # 'c' for current

            append_y_gap = False

            y_gap = yc_start - yp_end
            lh = self.get_single_line_height(line.coordinates)

            if FILTER_NEGATIVE_VALUE is True:
                if y_gap >= 0:
                    append_y_gap = True
                    if PRINT_OUTPUT is True:
                        print("Index:", line_index, "Gap:", y_gap)
            else:
                y_gaps.append(y_gap)
                append_y_gap = True
                if PRINT_OUTPUT is True:
                    print("Index:", line_index, "Gap:", y_gap)

            if append_y_gap:
                y_gaps.append(y_gap)
                if lh > 0:
                    line_heights.append(lh) # append line height only if the gap to previous line is positive (otherwise assume error)

        # generate borders for histogram segments
        bins = self.generate_bins(0, 3, 33)

        # d is an index array holding the bin id for each point in y_gaps
        assigned_digits = np.digitize(y_gaps, bins)
        hist, bin_edges = np.histogram(y_gaps, bins)
        median_bin = self.get_selected_bin_low_median(hist, bin_edges, assigned_digits, y_gaps)

        if do_analysis_stuff is True:
            # further methods and plots for comparison and analysis of best result

            # plot base histogram
            hp = histo_plotter.HistogramPlotter()
            hp.plot_histogram(y_gaps, bins)
            hp.plot_histogram_equally(y_gaps)

            histA, bin_edgesA = np.histogram(y_gaps, bins='auto')
            edge_maxA = self.get_selected_bin_low_median(histA, bin_edgesA, assigned_digits, y_gaps)

            histSqrt, bin_edgesSqrt = np.histogram(y_gaps, bins='sqrt')
            edge_maxSqrt = self.get_selected_bin_low_median(histSqrt, bin_edgesSqrt, assigned_digits, y_gaps)


        # calculate average line height
        lh_mean = int(np.round(np.mean(line_heights)))

        # length originally used array of line gaps, can be much shorter than number of line_heights,
        # cause no negative values are taken to account
        y_gaps_len = len(y_gaps)

        # length of used array for line heights calculation
        lh_len = len(line_heights)

        # calculate the average distance between to line middle points
        line_distance = median_bin + lh_mean

        if return_class is True:
            lhi = LineHeightInformation(line_distance, median_bin, lh_mean, y_gaps_len, lh_len)
            lhi.set_textfield(info_field)
            return lhi

        # return the calculated information
        return line_distance, median_bin, lh_mean, y_gaps_len, lh_len

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

    def get_selected_bin_low_median(self, hist, bin_edges, assigned_digits, original_values):
        """
        If there are multiple bins with the same occurence count detected as maximum, the lowest-value bin is taken
        :param hist:
        :param bin_edges:
        :param assigned_digits:
        :param original_values:
        :return:
        """
        PRINT_OUTPUT = False

        bin_max_index = np.where(hist == hist.max())
        refactored_index = bin_max_index[0].max()

        # special case: refactor maximum index, when there are multiple equal maximum values in histogram
        max_histo_value = hist[refactored_index]
        all_max_indices = []

        for hist_index, hist_value in enumerate(hist):
            if hist_value == max_histo_value:
                all_max_indices.append(hist_index)


        # adapt the index for special case, take the middle value in the distribution

        # my_custom_median_index = np.where(all_max_indices == np.median(all_max_indices))

        new_refactored_index = int(stats.median_low(all_max_indices))

        # additional condition for setting breakpoint
        if refactored_index != new_refactored_index:
            refactored_index = new_refactored_index

        values_in_this_bin = []
        for index_ad, ad in enumerate(assigned_digits):
            ad -= 1
            if ad == refactored_index:
                values_in_this_bin.append(original_values[index_ad])


        mean_val = np.mean(values_in_this_bin)
        final_mean = int(np.round(mean_val))
        return final_mean

        # detected_edges = bin_edges[bin_max_index]
        # detected_edge = detected_edges[0]

        # if PRINT_OUTPUT is True:
        #    print('maxbin', detected_edge)

        # return detected_edge

    def calculate_ld_information_tesseract(self, tesseract_page):

        # counters for final results

        # overall results
        overall_ldist = 0
        overall_gap_height = 0
        overall_line_height = 0

        # overall length counters
        overall_y_gaps_len = 0
        overall_line_height_len = 0


        for c_area in tesseract_page.areas:

            for c_paragraph in c_area.paragraphs:

                paragraph_line_count = len(c_paragraph.lines)

                # count in paragraph information, if it's only one line, don't count
                if paragraph_line_count >= 2:
                    ldist_paragraph, paragraph_gap_height, paragraph_line_height, paragraph_y_gaps_len, paragraph_lh_len = \
                                                    self.calculate_line_distance_information(c_paragraph.lines, False)

                    overall_ldist, unused = Random.add_to_mean(overall_ldist, ldist_paragraph, \
                                                               overall_line_height_len, paragraph_lh_len)


                    overall_gap_height, overall_y_gaps_len = Random.add_to_mean(overall_gap_height, paragraph_gap_height, \
                                                                                overall_y_gaps_len, paragraph_y_gaps_len)

                    overall_line_height, overall_line_height_len = Random.add_to_mean(overall_line_height, paragraph_line_height, \

                                                                                      overall_line_height_len, paragraph_lh_len)
                    #new_ovlh_counter = (overall_gap_height*overall_gap_count) +\
                    #                    (paragraph_gap_height*paragraph_line_count)
                    #new_ovlh_divisor = overall_gap_count + paragraph_line_count
                    #new_overall_line_height = new_ovlh_counter / new_ovlh_divisor
                    #overall_gap_height = new_overall_line_height
                    #overall_gap_count += paragraph_line_count




        final_ldist = TypeCasts.round_to_int(overall_ldist)
        final_gap_height = TypeCasts.round_to_int(overall_gap_height)
        final_line_height = TypeCasts.round_to_int(overall_line_height)
        # just for veriying final_ldist, slightly less inaccurate
        # final_ldist_2 = TypeCasts.round_to_int(final_gap_height + final_line_height)
        final_y_gaps_len = TypeCasts.round_to_int(overall_y_gaps_len)
        final_line_height_length = TypeCasts.round_to_int(overall_line_height_len)


        return final_ldist, final_gap_height, final_line_height, final_y_gaps_len, final_line_height_length

    def calculate_line_height_tesseract_simple(self, tesseract_page):

        all_lines = []

        for c_area in tesseract_page.areas:
            for c_paragraph in c_area.paragraphs:
                all_lines.extend(c_paragraph.lines)

        return self.calculate_line_distance_information(all_lines, False)


    def calculate_line_height_abbyy(self, abbyy_page):
        # todo: this function copys a lot of code from 'hocr_bbox_comparator-get_abbyy_boxes, refactor if possible

        html = abbyy_page._hocr_html
        contents = html.contents
        content_paragraphs = []

        for element in contents:
            res = str(element).find("ocr_line")
            if res >= 1:
                # in abbyy-hocr sometimes the lines are packed in ocr_careas and sometimes not
                # this reads all the lines in correct order
                if element.attrs['class'][0] == 'ocr_carea':
                    local_line_list = []
                    new_area = Area(None, element)
                    for par in new_area.paragraphs:
                        content_paragraphs.append(par)

                elif element.attrs['class'][0] == 'ocr_par':
                    local_line_list = []
                    par = Paragraph(None, element)
                    content_paragraphs.append(par)

                else:
                    raise Exception('THIS SHOULDNT HAPPEN!')


        mock_page = type('', (), {})()
        mock_page.areas = []
        mock_area = type('', (), {})()
        mock_area.paragraphs = content_paragraphs
        mock_page.areas.append(mock_area)


        return  self.calculate_ld_information_tesseract(mock_page)



