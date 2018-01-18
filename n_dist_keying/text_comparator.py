import difflib
from ocr_validation.ocrolib_edist import Edist3
from utils.typecasts import  TypeCasts
class TextComparator:
    @staticmethod
    def do_smth():
        print("it's done")


    @staticmethod
    def compare_tuples(tuple1, tuple2):

        # tuple1_string = ''.join(tuple1)
        # tuple2_string = ''.join(tuple2)

        tuple1_string = TypeCasts.tuple_to_string(tuple1)
        tuple2_string = TypeCasts.tuple_to_string(tuple2)

        if tuple1_string == tuple2_string:
            return 0, [], 0

        # edist = Edist3.levenshtein(tuple1_string, tuple2_string)
        strdif_ctr1, strdif1 = TextComparator.calculate_string_difference(tuple1_string, tuple2_string)
        # strdif_ctr2, strdif2 = TextComparator.calculate_string_difference(tuple2_string, tuple1_string)
        oc = TextComparator.calculate_string_order_confusion(tuple1_string, tuple2_string, strdif1)
        # print("t1", tuple1_string, "t2", tuple2_string, "strdif1", strdif1, "strdif2", strdif2)
        # if tuple1_string.find("51 70") >= 0:

        return strdif_ctr1, strdif1, oc


    @staticmethod
    def calculate_string_order_confusion(text1, text2, difference_indices):
        """
        A very simple measurement for the order confusion of characters in two strings,
        should only be used in combination with a similarity string-metric like levenstein-distance
        :param text1: input text 1, which is the reference text
        :param text2: input text 2, which is the text for comparison
        :return: float of normalized confusion 0 -> no confusion, higher values -> more confusion
        """

        tl_1 = list(text1)
        tl_2 = list(text2)
        tl_1c = tl_1[:]
        tl_2c = tl_2[:]
        accumulated_confusion = 0
        for char_1_index, char_1 in enumerate(tl_1c):
            for char_2_index, char_2 in enumerate(tl_2c):
                if char_1 is not None and char_2 is not None:
                    if char_1 == char_2:
                        match_distance = abs(char_1_index - char_2_index)
                        tl_1c[char_1_index] = None
                        tl_2c[char_2_index] = None
                        accumulated_confusion += match_distance
                        break # break inner loop

        normalized_confusion = accumulated_confusion / len(text1)
        return normalized_confusion




    @staticmethod
    def calculate_string_difference(text1, text2):
        """
        Simple difference of two strings:
        subtracts all chars from text1-text2, algorithm ignores order of characters
        returns the amount of different characters, as well as the indices of the difference characters
        (which are not correct in all cases cause order is ignored in subtraction)
        :param text1: input string 1
        :param text2: input string 2
        :return: the amount of different characters, as well as the indices of the difference characters

        """

        # search condition for debugging purposes
        #if text1.find("51 70") >= 0:
        #   print("found")

        tl_1 = list(text1)
        tl_2 = list(text2)
        tl_1c = tl_1[:]
        tl_2c = tl_2[:]

        for char_1_index, char_1 in enumerate(tl_1c):
            for char_2_index, char_2 in enumerate(tl_2c):
                if char_2 is not None and char_1 == char_2:
                    tl_1c[char_1_index] = None
                    tl_2c[char_2_index] = None
                    break # break inner loop

        # all occurences are now tagged, extract difference indices and diffence counter
        difference_indices = []
        difference_count = 0
        for char_1_index, char_1 in enumerate(tl_1c):
            if char_1 is not None:
                difference_count += 1
                difference_indices.append(char_1_index)

        if difference_count == 1:
            print("yes")


        return difference_count, difference_indices

    @staticmethod
    def compare_ocr_strings_difflib_seqmatch(ocr_string1, ocr_string2):
        """
        difflib sequence matching is based on Ratcliff and Obershelp algorithm
        longest contiguous matching subsequence that contains no “junk” elements

        :param ocr_string1:
        :param ocr_string2:
        :return:
        """
        sqmatch = difflib.SequenceMatcher(None, ocr_string1, ocr_string2, True)
        ratio = sqmatch.ratio()

        # matching_blocks = sqmatch.get_matching_blocks() # necessary
        """
        for idx, block in enumerate(matching_blocks):
            (str1_starti, str2_starti, match_length) = block

            str1_substr = ocr_string1[str1_starti:str1_starti+match_length]
            str2_substr = ocr_string2[str2_starti:str2_starti+match_length]

            print("Block ",str(idx).zfill(4),"str1 match: ",str1_substr)
            print("Block ",str(idx).zfill(4),"str2 match: ",str2_substr)

        # similarity of sequences info
        """
        # ratio = sqmatch.ratio()
        distance = 1 - ratio

        return distance

    @staticmethod
    def compare_ocr_strings_cwise(ocr_string1, ocr_string2, ignore_case=False):
        """
        Character-wise comparison of ocr strings
        :param ocr_string1: input string 1
        :param ocr_string2: input string 2
        :param ignore_case: if True, no case sensivity, cast everything (including result) to lowercase
        :return: ocr_string1 subtracted by the characters in ocr_string2
        """

        # simple method for ignore case, just downcast everything to lowercase
        if ignore_case:
            ocr_string1 = ocr_string1.lower()
            ocr_string2 = ocr_string2.lower()

        final_string = ocr_string1
        for char in ocr_string2:
            foundindex = final_string.find(char)
            if foundindex >= 0:
                # final_string_old = final_string.replace(char, ' ') #erroronous replaces all strings
                final_string = final_string.replace(char, ' ', 1)

        return final_string

    @staticmethod
    def compare_ocr_strings_difflib_seqmatch_old(ocr_string1, ocr_string2):
        """
        difflib sequence matching is based on Ratcliff and Obershelp algorithm
        longest contiguous matching subsequence that contains no “junk” elements

        :param ocr_string1:
        :param ocr_string2:
        :return:
        """
        sqmatch = difflib.SequenceMatcher(None, ocr_string1, ocr_string2, True)

        matching_blocks = sqmatch.get_matching_blocks()
        for idx, block in enumerate(matching_blocks):
            (str1_starti, str2_starti, match_length) = block

            str1_substr = ocr_string1[str1_starti:str1_starti + match_length]
            str2_substr = ocr_string2[str2_starti:str2_starti + match_length]

            print("Block ", str(idx).zfill(4), "str1 match: ", str1_substr)
            print("Block ", str(idx).zfill(4), "str2 match: ", str2_substr)

        # similarity of sequences info
        ratio = sqmatch.ratio()
        print("Similarity ratio is ", ratio)

        # find longest match in a subsequence of strings
        longest_match = sqmatch.find_longest_match(0, 10, 5, 10)

        # operations how to turn ocrstr1 into ocrstr2
        opcodes = sqmatch.get_opcodes()
        opcodes_grouped = sqmatch.get_grouped_opcodes(3)

    @staticmethod
    def compare_ocr_strings_difflib_difftool(ocr_string1, ocr_string2):
        print("compare ocr strings ")
        differ = difflib.Differ(None, None)
        cres = differ.compare(ocr_string1, ocr_string2)
        listres = list(cres)

        print("differ results ")
        for element in listres:
            ctrl_char = element[0:1]
            string = element[1::]
            print("Control char: ", ctrl_char, " text: ", string)

        """
            Codes in differ result
            '- ' 	line unique to sequence 1
            '+ ' 	line unique to sequence 2
            '  ' 	line common to both sequences
            '? ' 	line not present in either input sequence
        """

        # Alternative ndiff
        print("ndiff results ")
        ndiff = difflib.ndiff(ocr_string1, ocr_string2)
        ndiflist = list(ndiff)

        for element in ndiflist:
            ctrl_char = element[0:1]
            string = element[1::]
            print("Control char: ", ctrl_char, " text: ", string)