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


        if CORRECT_ROMAN_II:
            line_text = TextCorrector.correct_roman_ii(line_text)


        return line_text

    @staticmethod
    def correct_roman_ii(line_text):
        """
        todo: this correction has to be verified for false positives 
        Corrects occurrences of roman II letters which get confused with I1 or 11 sometimes

        Example:
        Groundtruth: 1948/II/49 bis 1954: je 0 %
        line_text  : 1948/11/49 bis 1954: je 0%

        :param line_text:
        :return:
        """

        # check if the date pattern occurs
        # \d: Matches any decimal digit
        # \w: Matches any alphanumeric character (alphabet or number)

        rii_regex = re.compile('\d\d\d\d/\w\w/\d\d')
        rii_match = rii_regex.match(line_text)

        # return the unchanged text, if the pattern doesn't occur
        if rii_match is None:
            return line_text

        # if the pattern occurs, refactor line_text (todo: this is simple-mode replacement, make it better)
        rii_string = rii_match.group()
        rii_string = rii_string.replace('/11/', '/II/')
        rii_string = rii_string.replace('/I1/', '/II/')
        rii_string = rii_string.replace('/1I/', '/II/')

        # substitute the corrected text in original string
        new_line_text = rii_regex.sub(rii_string, line_text)

        return new_line_text