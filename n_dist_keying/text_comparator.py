import difflib


class TextComparator:
    @staticmethod
    def do_smth():
        print("it's done")

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