"""
Contains various corrections for text from ocr file
"""

import re

class TextCorrector(object):

    def __init__(self):
        print("init corrector")

    @staticmethod
    def correct_line_text(line_text):
        CORRECT_ROMAN_II = True
        CORRECT_EXLAMATIONS = False

        if CORRECT_ROMAN_II:
            line_text = TextCorrector.correct_roman_ii(line_text)
        if CORRECT_EXLAMATIONS:
            line_text = TextCorrector.correct_exclamation_marks(line_text)

        return line_text


    @staticmethod
    def correct_exclamation_marks(line_text):
        if line_text is None or line_text is False or line_text is True:
            return line_text

        DEFAULT_REPLACEMENT = "\""
        possible_exclamation_combos = \
            ["'\"", "\"'", "''", "\"\""]

        def do_correction(line_text, pec):
            line_text_new = line_text.replace(pec, DEFAULT_REPLACEMENT)
            return line_text_new

        for pec in possible_exclamation_combos:

            if pec in line_text:
                line_text = do_correction(line_text, pec)

        return line_text

    @staticmethod
    def correct_roman_ii(line_text):
        """
        Corrects occurrences of roman II letters which get confused with I1 or 11 sometimes

        Example:
        Groundtruth: 1948/II/49 bis 1954: je 0 %
        line_text  : 1948/11/49 bis 1954: je 0%
        or
        Groundtruth: II/1955/42 text text
        line_text:   1I/1955/42 text text

        :param line_text:
        :return:
        """



        # check if the possibly erronous line occurs:
        # if the first 2 or more characters are 1, or I, or l, or i
        # and following 3 or more are decimals, and following 2 or more are decimals
        # (seperated by slashes)
        rii_regex = re.compile('[1Ili]{2,}\/\d{3,}/\d{2,}')
        rii_match = rii_regex.match(line_text)

        rii_regex2 = re.compile('\d{4,}\/[1Ili]{2}/\d{2,}')
        rii_match2 = rii_regex2.match(line_text)


        # return the changed text, if the pattern   occurs
        if rii_match is not None:
            subst_string = re.sub('[1Ili]{2,}\/', "II/", line_text)
            # place the corrected roman two in line_text
            return subst_string
        elif rii_match2 is not None:
            # todo verify this once with bp the case definitely exists but not in manyyears
            subst_string = re.sub('[1Ili]{2}\/', "II/", line_text)
            # place the corrected roman two in line_text
            return subst_string

        # return unchanged if pattern doesn't occur
        return line_text