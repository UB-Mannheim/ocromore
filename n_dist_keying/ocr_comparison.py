class OCRcomparison:
    """
        Storage class for multiple Ocr_Sets
    """

    def __init__(self):
        self.ocr_sets = []

    def add_set(self,set_to_add):
        self.ocr_sets.append(set_to_add)

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


    def unspace_sets(self):
        for set in self.ocr_sets:
            set.unspace_lines()



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

    def save_n_distance_keying_results_to_file(self,filename):
        file = open(filename, 'w+')

        for  current_set in self.ocr_sets:
            sd_line = current_set.get_shortest_n_distance_line()

            # do not print lines which are mostly recognized with no content at the moment
            if sd_line is not None and sd_line is not False:
                file.write(sd_line+"\n")

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