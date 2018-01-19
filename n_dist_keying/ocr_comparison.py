from utils.typecasts import TypeCasts
from utils.random import Random

class OCRcomparison:
    """
        Storage class for multiple Ocr_Sets
    """

    def __init__(self):
        self.ocr_sets = []
        self.line_height_information = []

    def add_set(self, set_to_add):
        self.ocr_sets.append(set_to_add)

    def add_line_information(self, line_height_information):
        self.line_height_information.append(line_height_information)

    def sort_set(self):
        """
        Sort the ocr_sets by y_mean values
        :return:
        """
        def take_y_mean(my_set):
            ym = my_set.y_mean
            return ym

        sorted_sets = sorted(self.ocr_sets, key=take_y_mean, reverse=False)
        self.ocr_sets = sorted_sets


    def unspace_list(self, list_index_to_unspace, unspaced_list_index):
        """
        apply the unspacing algorithm to one of the lists, take another list as
        comparison  (which is not spaced)
        :param list_index_to_unspace: index for the set to unspace
        :param unspaced_list_index: index for the non-spaced set
        :return:
        """

        for set in self.ocr_sets:
            set.unspace_lines(list_index_to_unspace, unspaced_list_index)

    def refspace_list(self, list_index_to_adapt, list_index_reference):

        for set in self.ocr_sets:
            set.refspace_lines( list_index_to_adapt, list_index_reference )

    def print_sets(self, diff_only= False):
        for current_set in self.ocr_sets:
            current_set.print_me(diff_only)

    def do_n_distance_keying(self):
        for current_set in self.ocr_sets:
            current_set.calculate_n_distance_keying()

    def print_n_distance_keying_results(self):
        print("N_DISTANCE_KEYING_RESULTS ")
        for current_set in self.ocr_sets:
            current_set.print_shortest_n_distance_line()

    def add_linebreaks(self, previous_line, current_line, previous_line_index, sd_line_index, line_heigth_info):
        MODE = 'TAKE_CURRENT_LINE_DIST'

        if previous_line is None:
            return None
        if MODE is 'TAKE_CURRENT_LINE_DIST':
            MARGIN = 0 # tolerance margin
            current_lh_info = line_heigth_info[sd_line_index]
            (xp_start, yp_start, xp_stop, yp_stop) = previous_line.coordinates
            (xc_start, yc_start, xc_stop, yc_stop) = current_line.coordinates

            y_dist = yc_start - yp_stop

            if y_dist <= 0:
                return None

            line_distance = current_lh_info.get_line_distance()
            y_times = (y_dist + MARGIN) / line_distance
            y_times_absolute = TypeCasts.round_to_int(y_times)
            if y_times_absolute > 0:
                generated_text = Random.append_pad_values("",y_times_absolute,"\n")
                return generated_text
            else:
                return None



        print("Undefined case reached shouldn't happen")
        return None

    def save_n_distance_keying_results_to_file(self,filename, mode_add_linebreaks=False):
        file = open(filename, 'w+')

        previous_sd_line = None
        previous_sd_line_index = None
        for current_set in self.ocr_sets:

            sd_text = current_set.get_shortest_n_distance_text()
            # add comparison from previous to actual line break here
            if mode_add_linebreaks:
                sd_line_index = current_set.get_shortest_n_distance_index()
                sd_line = current_set.get_shortest_n_distance_line()
                if sd_line is True or sd_line is False:
                    continue

                additional_breaks = \
                    self.add_linebreaks(previous_sd_line, sd_line, previous_sd_line_index, sd_line_index, self.line_height_information)

                if additional_breaks is not None:
                    file.write(additional_breaks)
                previous_sd_line = sd_line
                previous_sd_line_index = sd_line_index

            # do not print lines which are mostly recognized with no content at the moment
            if sd_text is not None and sd_text is not False:
                file.write(sd_text+"\n")


        file.close()


    def save_dataset_to_file(self, filename, set_index, mode_add_linebreaks = False):
        file = open(filename, 'w+')

        previous_dataset_line = None
        previous_dataset_line_index = None

        for current_set in self.ocr_sets:

            dataset_text = current_set.get_line_set_value_text(set_index)

            # add comparison from previous to actual line break here
            if mode_add_linebreaks:
                dataset_line = current_set.get_line_set_value_line(set_index)
                if dataset_line is True or dataset_line is False:
                    continue

                additional_breaks = \
                    self.add_linebreaks(previous_dataset_line, dataset_line, previous_dataset_line_index, set_index,
                                        self.line_height_information)

                if additional_breaks is not None:
                    file.write(additional_breaks)
                previous_dataset_line = dataset_line
                previous_dataset_line_index = set_index

            # do not print lines which are mostly recognized with no content at the moment
            if dataset_text is not None and dataset_text is not False:
                file.write(dataset_text + "\n")

        file.close()

    def export_text_lines(self):
        """
        Exports the lines of text of the result as list
        :return: list with lines
        """

        return_list = []
        for setindex, current_set in enumerate(self.ocr_sets):
            sd_line = current_set.get_shortest_n_distance_line()

            # do not list lines which are mostly recognized with no content at the moment
            if sd_line is not None and sd_line is not False:
                return_list.append(sd_line)

        return sd_line