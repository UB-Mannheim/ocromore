from utils.queues import Ranged_Filo
from utils.random import Random


class TextUnspacer:
    """
        Class which helps to filter out spaced text like this ('s p a c e d' with a comparison text like 'spaced')
        #todo unspace_text can be improved, sometimes repeating patterns like ultimo ultimo 1998, in comparison to ultimo 1998 produce weird results
        #todo ...this can be filtered or the matching parts of both strings can be compared, non matched part acts as a rest
    """

    def get_tuples(self, text, size_filo, search_range_filo):

        text_split = list(text)
        text_split_size = len(text_split)
        # print("Text is ", text)
        tuples_list = []
        tuples_adjacent_list = []

        # pad up the rest, for fifo clearance
        for i in range(0, size_filo+2):
            text_split.append('¦')

        current_chars_filo = Ranged_Filo(size_filo+2, search_range_filo, True)


        for index_char, char in enumerate(text_split):
            current_chars_filo.push(char)
            middle_items = current_chars_filo.get_middle_items_for_range(search_range_filo)
            middle_items_adjacent = current_chars_filo.get_middle_items_for_range(search_range_filo+1)
            current_size = current_chars_filo.size()

            # wait until filo is filled, unless the amount of chars is smaller than filo
            if current_size < size_filo and text_split_size >= size_filo:
                continue

            if middle_items_adjacent[current_chars_filo.get_middle_index()] is ' ':
                # print("Index_char:", index_char, "Char: ", char, "Tuple:", middle_items)
                tuples_list.append(middle_items)
                tuples_adjacent_list.append(middle_items_adjacent)

        return tuples_list, tuples_adjacent_list

    def add_adjacent_tuple_information(self, tuples, tuples_with_adjacent_info):

        final_tuple_list = []
        change = False

        for tuple_index, tuple in enumerate(tuples):
            tuplec = tuple[:]
            tuplec_with_adjacent_info = tuples_with_adjacent_info[tuple_index][:]

            tuplec_low_end = tuplec[0]
            tuplec_high_end = tuple[len(tuple)-1]
            tupleca_low_end = tuplec_with_adjacent_info[0]
            tupleca_high_end = tuplec_with_adjacent_info[len(tuplec_with_adjacent_info)-1]

            if tuplec_low_end == ' ':
                if tupleca_low_end != None and tupleca_low_end != ' ':
                    tuplec = Random.replace_value_in_tuple(tuplec, tupleca_low_end, 0)
                    change = True

            if tuplec_high_end == ' ':
                if tupleca_high_end != None and tupleca_low_end !=' ':
                    tuplec = Random.replace_value_in_tuple(tuplec, tupleca_high_end, len(tuplec)-1)
                    change = True

            final_tuple_list.append(tuplec)


        return final_tuple_list, change


    def unspace_texts(self, text_list, list_index_to_unspace, unspaced_list_index):

        PRINT_OUTPUT = False
        SEARCH_RANGE_FILO = 1
        SIZE_FILO = 3
        WILDCARD_MODE = True  # possibility to tolerate a certain amount of errors in subtraction of arrays
        WILDCARD_COUNT = 2  # amount of errors tolerated with wildcards

        if WILDCARD_MODE:
            SEARCH_RANGE_FILO = 2
            SIZE_FILO = 5


        line_to_process = text_list[list_index_to_unspace]
        line_unspaced = text_list[unspaced_list_index]

        # just return if there is no text for comparison
        if not hasattr(line_to_process, 'ocr_text_normalized') \
                or not hasattr(line_unspaced, 'ocr_text_normalized'):
            return text_list


        text = line_to_process.ocr_text_normalized
        text_cmp = line_unspaced.ocr_text_normalized

        if "Aus den G" in text_cmp:
            print("im here")

        text_tuple, text_tuple_adj = self.get_tuples(text, SIZE_FILO, SEARCH_RANGE_FILO)
        text_tuple_cmp, text_tuple_cmp_adj = self.get_tuples(text_cmp, SIZE_FILO, SEARCH_RANGE_FILO)
        if WILDCARD_MODE:
            text_tuple2, change1 = self.add_adjacent_tuple_information(text_tuple, text_tuple_adj)
            text_tuple_cmp2, change2 = self.add_adjacent_tuple_information(text_tuple_cmp, text_tuple_cmp_adj)
            if change1 or change2:
                print("test")

        print("text", text, "text_cmp", text_cmp)
        diff1 = Random.subtract_arrays(text_tuple, text_tuple_cmp, WILDCARD_MODE, WILDCARD_COUNT, text_tuple2, text_tuple_cmp2)

        if len(text_tuple) != len(text_tuple2):
            print("test")


        # put text to process together with the process information
        text_unspaced = self.create_non_spaced_string(text, diff1, SIZE_FILO, SEARCH_RANGE_FILO)
        
        if PRINT_OUTPUT:
            print("US-> line:", text)
            print("US-> cmpr:", text_cmp)
            print("US-> uspc:", text_unspaced)

        # apply to list again
        text_list[list_index_to_unspace].ocr_text_normalized = text_unspaced
        return text_list

    def create_non_spaced_string(self, text, diff_tuples, size_filo, search_range_filo):

        PADDING_CHAR = '¦'
        # pad values because of filos
        text_padded = Random.append_pad_values(text, size_filo, PADDING_CHAR)

        text_split = list(text_padded)
        current_chars_filo = Ranged_Filo(size_filo, search_range_filo, True)
        filo_mid_index = current_chars_filo.get_middle_index()
        final_text = ""

        for char_index, char in enumerate(text_split):
            current_chars_filo.push(char)
            # if current middle char is ' ' and there is a diff tuple for that, don't push it to final string
            current_tuple = current_chars_filo.get_middle_items(True, True)
            current_middle_char = current_tuple[filo_mid_index]
            its_a_diff_tuple = False
            for diff_tuple_index, diff_tuple in enumerate(diff_tuples):
                if current_tuple == diff_tuple:
                    diff_tuples[diff_tuple_index] = "done"   # mark this tuple as corrected
                    its_a_diff_tuple = True
                    break  # escape inner loop

            if current_middle_char is not PADDING_CHAR:  # do not append padded chars
                if not its_a_diff_tuple and current_middle_char is not None:
                    final_text += current_middle_char

        return final_text

