from n_dist_keying.text_comparator import TextComparator


class Random:

    @staticmethod
    def replace_value_in_tuple(tuple_in, value, index):
        tuple_l = list(tuple_in)  # make a[0] mutable
        tuple_l[index] = value  # now new assignment will be valid
        ret_val= tuple(tuple_l)  # make a[0] again a tuple
        return ret_val


    @staticmethod
    def append_pad_values(text, padding_length, padding_char='¦'):

        new_text = text
        for index in range(0, padding_length):
            new_text += padding_char

        return new_text

    @staticmethod
    def find_middle(length_of_list, to_lower):
        """
        Finds the middle index of a list
        :return: middle index if list has unequal size. lower and higher index tuple is equal sitze
        """

        middle = float(length_of_list)/2
        if middle % 2 != 0:
            return int(middle - .5)
        else:
            low_middle = int(middle-1)
            high_middle = int(middle)

            if to_lower:
                return low_middle
            else:
                return (low_middle, high_middle)

    @staticmethod
    def subtract_arrays(arr1_in, arr2_in, wildcard_mode=False, wildcard_count=0, arr1_in_adj=[], arr2_in_adj=[]):
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
            for index_a2, entry_a2 in enumerate(arr2):

                entry_a1_adj = None
                entry_a2_adj = None

                if wildcard_mode:
                    entry_a1_adj = arr1_in_adj[index_a1]
                    entry_a2_adj = arr2_in_adj[index_a2]

                if wildcard_mode is False:
                    if entry_a1 is not None and entry_a1 == entry_a2:
                        arr1[index_a1] = None
                        arr2[index_a2] = None
                        break
                else:
                    if entry_a1 is not None and entry_a2 is not None:
                        tpldif_ctr, tpldif, order_confusion = TextComparator.compare_tuples(entry_a1, entry_a2)
                        if tpldif_ctr <= wildcard_count:
                            if tpldif_ctr != 0:
                                # additional condition, the string shouldn't be order confused
                                print("1st", entry_a1)
                                print("2nd", entry_a2)
                                print("order_confusion", order_confusion)
                                if order_confusion > ORDER_CONFUSION_TRESHOLD:
                                    continue
                                tpldif_ctr2, tpldif2, order_confusion2 = TextComparator.compare_tuples(entry_a1_adj, entry_a2)
                                if tpldif_ctr2 == 0:
                                    # this means the adjusted version is equal and this is a match
                                    arr1[index_a1] = None
                                    arr2[index_a2] = None
                                    break


                            arr1[index_a1] = None
                            arr2[index_a2] = None
                            break
                        #res1 = TextComparator.compare_ocr_strings_difflib_seqmatch(entry_a1, entry_a2)
                        #res2 = TextComparator.compare_ocr_strings_difflib_difftool(entry_a1, entry_a2)
                        #print("done")

        # subtract nones from arr1
        arr1_reduced = [value for value in arr1 if value is not None]

        return arr1_reduced

    @staticmethod
    def add_to_mean(overall_value, current_value, overall_count, current_count):
        """
        Adds a mean of a number of values to an existing mean, and adapts the outcoming mean
        based on the number of the additional values
        :param overall_value: overall mean
        :param current_value: additional value to add
        :param overall_count: number of values the original mean was calculated
        :param current_count: number of values the additional mean was calculated
        :return: new calculated mean, new number of values
        """

        new_overall_counter = (overall_value * overall_count) + \
                           (current_value * current_count)
        new_overall_divisor = overall_count + current_count
        new_overall_value = new_overall_counter / new_overall_divisor
        new_overall_count = overall_count + current_count
        return new_overall_value, new_overall_count
