

class Random:

    @staticmethod
    def printc(*args, print_output):
        """
        Print conditionally if print_output is True 
        :param args:
        :param print_output:
        :return:
        """
        if print_output is True:
            print(*args)


    @staticmethod
    def is_false_true_or_none(value):
        if value is False or value is True or value is None:
            return True

        return False

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
