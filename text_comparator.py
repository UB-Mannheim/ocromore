import difflib


class TextComparator:

    @staticmethod
    def compare_ocr_strings_difflib_seqmatch(ocr_string1, ocr_string2):
        """
        difflib sequence matching is based on Ratcliff and Obershelp algorithm
        longest contiguous matching subsequence that contains no “junk” elements

        :param ocr_string1:
        :param ocr_string2:
        :return:
        """
        sqmatch = difflib.SequenceMatcher(None,ocr_string1,ocr_string2,True)

        matching_blocks = sqmatch.get_matching_blocks()
        for idx, block in enumerate(matching_blocks):
            (str1_starti, str2_starti, match_length) = block

            str1_substr = ocr_string1[str1_starti:str1_starti+match_length]
            str2_substr = ocr_string2[str2_starti:str2_starti+match_length]

            print("Block ",str(idx).zfill(4),"str1 match: ",str1_substr)
            print("Block ",str(idx).zfill(4),"str2 match: ",str2_substr)

        # similarity of sequences info
        ratio = sqmatch.ratio()
        return ratio