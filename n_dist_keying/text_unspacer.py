from utils.queues import Ranged_Filo
from utils.random import Random
from utils.typecasts import TypeCasts
from n_dist_keying.text_comparator import TextComparator


class TextUnspacer:
    """
        Class which helps to filter out spaced text like this ('s p a c e d' with a comparison text like 'spaced')
        #todo unspace_text can be improved, sometimes repeating patterns like ultimo ultimo 1998, in comparison to ultimo 1998 produce weird results
        #todo ...this can be filtered or the matching parts of both strings can be compared, non matched part acts as a rest
    """

    def get_tuples(self, text, size_filo, search_range_filo, non_spaced_only = False):

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

            if non_spaced_only is False:
                if middle_items_adjacent[current_chars_filo.get_middle_index()] is ' ':
                    # print("Index_char:", index_char, "Char: ", char, "Tuple:", middle_items)
                    tuples_list.append(middle_items)
                    tuples_adjacent_list.append(middle_items_adjacent)
            else:
                if middle_items_adjacent[current_chars_filo.get_middle_index()] is not ' ':
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

        # if "Aus den G" in text_cmp:
        #    print("im here")

        text_tuple, text_tuple_adj = self.get_tuples(text, SIZE_FILO, SEARCH_RANGE_FILO)
        text_tuple_cmp, text_tuple_cmp_adj = self.get_tuples(text_cmp, SIZE_FILO, SEARCH_RANGE_FILO)
        if WILDCARD_MODE:
            text_tuple2, change1 = self.add_adjacent_tuple_information(text_tuple, text_tuple_adj)
            text_tuple_cmp2, change2 = self.add_adjacent_tuple_information(text_tuple_cmp, text_tuple_cmp_adj)
            # if change1 or change2:
            # print("test")

        print("text", text, "text_cmp", text_cmp)
        diff1 = self.subtract_arrays(text_tuple, text_tuple_cmp, WILDCARD_MODE, WILDCARD_COUNT, text_tuple2,0)

        # if len(text_tuple) != len(text_tuple2):
        # print("test")

        # put text to process together with the process information
        text_unspaced = self.create_non_spaced_string(text, diff1, SIZE_FILO, SEARCH_RANGE_FILO)

        if PRINT_OUTPUT:
            print("US-> line:", text)
            print("US-> cmpr:", text_cmp)
            print("US-> uspc:", text_unspaced)

        # apply to list again
        text_list[list_index_to_unspace].ocr_text_normalized = text_unspaced
        return text_list


    def refspace_texts(self, text_list, list_index_to_process, list_index_reference):

        PRINT_OUTPUT = False
        SEARCH_RANGE_FILO = 1
        SIZE_FILO = 3
        WILDCARD_MODE = True  # possibility to tolerate a certain amount of errors in subtraction of arrays
        WILDCARD_COUNT = 2  # amount of errors tolerated with wildcards

        if WILDCARD_MODE:
            SEARCH_RANGE_FILO = 2
            SIZE_FILO = 5


        line_to_process = text_list[list_index_to_process]
        line_reference = text_list[list_index_reference]

        # just return if there is no text for comparison
        if not hasattr(line_to_process, 'ocr_text_normalized') \
                or not hasattr(line_reference, 'ocr_text_normalized'):
            return text_list


        text = line_to_process.ocr_text_normalized
        text_reference = line_reference.ocr_text_normalized

        # text = "der A u f s i c h t s ra t hier ist"
        # text_reference = "der Aufsichtsrat hier i s t"


        #if "Aus den G" in text_cmp:
        #    print("im here")

        text_tuple, text_tuple_adj = self.get_tuples(text, SIZE_FILO, SEARCH_RANGE_FILO)
        text_tuple_nonsp, text_tuple_adj_nonsp = self.get_tuples(text, SIZE_FILO, SEARCH_RANGE_FILO, True)

        text_tuple_ref, text_tuple_cmp_adj = self.get_tuples(text_reference, SIZE_FILO, SEARCH_RANGE_FILO)
        text_tuple_ref_nonsp, text_tuple_cmp_adj_nonsp = self.get_tuples(text, SIZE_FILO, SEARCH_RANGE_FILO, True)

        if WILDCARD_MODE:
            text_tuple_with_adj, change1 = self.add_adjacent_tuple_information(text_tuple, text_tuple_adj)
            text_tuple_ref2, change2 = self.add_adjacent_tuple_information(text_tuple_ref, text_tuple_cmp_adj)
            text_tuple2_nonsp, change1_nonsp = self.add_adjacent_tuple_information(text_tuple_nonsp, text_tuple_adj_nonsp)
            text_tuple_ref2_nonsp, change2_nonsp = self.add_adjacent_tuple_information(text_tuple_ref_nonsp, text_tuple_cmp_adj_nonsp)


            # if change1 or change2:
                # print("test")

        print("text", text, "text_cmp", text_reference)
        diff1 = self.subtract_arrays(text_tuple, text_tuple_ref, WILDCARD_MODE, WILDCARD_COUNT, text_tuple_with_adj, 0)
        diff2 = self.subtract_arrays(text_tuple_ref, text_tuple, WILDCARD_MODE, WILDCARD_COUNT, text_tuple_with_adj, 1)

        # if len(text_tuple) != len(text_tuple2):
            # print("test")


        # put text to process together with the process information
        text_unspaced = self.create_non_spaced_string(text, diff1, SIZE_FILO, SEARCH_RANGE_FILO)
        text_final = self.create_spaced_string(text_unspaced, diff2, SIZE_FILO, SEARCH_RANGE_FILO)

        if PRINT_OUTPUT:
            print("RS-> line:", text)
            print("RS-> refr:", text_reference)
            print("RS-> uspc:", text_unspaced)
            print("RS-> rspc:", text_final)

        # apply to list again
        text_list[list_index_to_process].ocr_text_normalized = text_final
        return text_list


    def create_spaced_string(self, text, diff_tuples, size_filo, search_range_filo):

        PADDING_CHAR = '¦'
        MID_FILL_CHAR = '¯'

        final_text = text

        for current_tuple in diff_tuples:
            current_tuple_list = list(current_tuple)
            middle_index_list = Random.find_middle(len(current_tuple_list),True)
            current_tuple_list[middle_index_list] = MID_FILL_CHAR
            stringed_tuple = TypeCasts.list_to_string(current_tuple_list)
            stringed_tuple = stringed_tuple.strip() # trim outbound spaces
            stringed_tuple = stringed_tuple.replace(PADDING_CHAR, '')
            stringed_tuple_final = stringed_tuple.replace(MID_FILL_CHAR, '')
            stringed_replacement = stringed_tuple.replace(MID_FILL_CHAR,' ')
            # found_in_text = text.find(stringed_tuple_final)

            new_text = final_text.replace(stringed_tuple_final, stringed_replacement)
            final_text = new_text


        return final_text


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

    def subtract_arrays(self, arr1_in, arr2_in, wildcard_mode=False, wildcard_count=0, arr_ref_in_adj=[], non_reference_switch=0):
        """
        Subtract arr2 from arr1 (arr1-arr2), same contents get subtracted once
        i.e. arr1 = ['a','a','b'], arr2 = ['a'], result is ['a', 'b']
        :param arr1_in: input list one
        :param arr2_in: input list two
        :return: subtracted output
        """
        ORDER_CONFUSION_TRESHOLD = 0.4

        # create copies of input arrays, which can be modified
        arr1 = arr1_in[:]
        arr2 = arr2_in[:]

        # mark everything which is equal once
        for index_a1, entry_a1 in enumerate(arr1):
            if index_a1 == 12:
                print("reachd breaking point")

            for index_a2, entry_a2 in enumerate(arr2):




                entry_ref_adj = None
                #entry_a2_adj = None

                if wildcard_mode:
                    used_ref_index = -1
                    if non_reference_switch == 0:
                        used_ref_index = index_a1
                    else:
                        used_ref_index = index_a2

                    if len(arr_ref_in_adj) <= used_ref_index:
                        print("what")

                    entry_ref_adj = arr_ref_in_adj[used_ref_index]
                    #entry_a2_adj = arr2_in_adj[index_a2]

                if wildcard_mode is False:
                    if entry_a1 is not None and entry_a1 == entry_a2:
                        arr1[index_a1] = None
                        arr2[index_a2] = None
                        break
                else:
                    if entry_a1 is not None and entry_a2 is not None:
                        tpldif_ctr, tpldif, order_confusion = TextComparator.compare_tuples(entry_a1, entry_a2)
                        if tpldif_ctr <= wildcard_count:
                            if order_confusion > ORDER_CONFUSION_TRESHOLD:
                                continue

                            if tpldif_ctr != 0:
                                # additional condition, the string shouldn't be order confused
                                print("1st", entry_a1)
                                print("2nd", entry_a2)
                                #if order_confusion > ORDER_CONFUSION_TRESHOLD:
                                #    continue
                                if non_reference_switch == 0:
                                    tpldif_ctr2, tpldif2, order_confusion2 = TextComparator.compare_tuples(entry_ref_adj, entry_a2)
                                else:
                                    tpldif_ctr2, tpldif2, order_confusion2 = TextComparator.compare_tuples(entry_ref_adj, entry_a1)

                                if tpldif_ctr2 == 0:
                                    # this means the adjusted version is equal and this is a match
                                    arr1[index_a1] = None
                                    arr2[index_a2] = None
                                    break
                                else:
                                    continue # else don't remove cause no match, search on

                            arr1[index_a1] = None
                            arr2[index_a2] = None
                            break
                        #res1 = TextComparator.compare_ocr_strings_difflib_seqmatch(entry_a1, entry_a2)
                        #res2 = TextComparator.compare_ocr_strings_difflib_difftool(entry_a1, entry_a2)
                        #print("done")

        # subtract nones from arr1
        arr1_reduced = [value for value in arr1 if value is not None]

        return arr1_reduced
