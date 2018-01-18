class TypeCasts:

    @staticmethod
    def round_to_int(value):
        return int(round(value))

    @staticmethod
    def tuple_to_string(input_tuple, none_replacement=True, none_replacer_char='¦'):
        val_lst = list(input_tuple)
        final_string = ""
        for value in val_lst:
            if none_replacement:
                if value == None:
                    final_string += none_replacer_char
                    continue

            final_string += value

        return final_string