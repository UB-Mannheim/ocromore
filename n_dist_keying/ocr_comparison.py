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



