class TypeCasts:

    @staticmethod
    def convert_string_to_unicode_list(text):

        unicode_a = []
        for char in list(text):
            # echar = char.encode('UTF-16')
            ordinal = ord(char)
            unicode_a.append(ordinal)
        return unicode_a


    @staticmethod
    def convert_unicodelist_to_string(u_list):

        text = ""
        for number in list(u_list):
            # echar = char.encode('UTF-16')
            character = chr(number)
            text += character
        return text


    @staticmethod
    def round_to_int(value):
        return int(round(value))

    @staticmethod
    def tuple_to_string(input_tuple, none_replacement=True, none_replacer_char='¦'):
        val_lst = list(input_tuple)
        final_string = TypeCasts.list_to_string(val_lst, none_replacement, none_replacer_char)
        return final_string

    @staticmethod
    def list_to_string(input_list, none_replacement=True, none_replacer_char='¦'):
        final_string = ""
        for value in input_list:
            if none_replacement:
                if value == None:
                    final_string += none_replacer_char
                    continue

            final_string += value

        return final_string