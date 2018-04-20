from skbio.sequence import GrammaredSequence
from skbio.util import classproperty
import string
#Out[2]: TypeError("local_pairwise_align() missing 3 required positional arguments: 'gap_open_penalty', 'gap_extend_penalty', and 'substitution_matrix'")

class CustomSequence(GrammaredSequence):

    blosum50 = \
        {
            '*': {'*': 1, 'A': -5, 'C': -5, 'B': -5, 'E': -5, 'D': -5, 'G': -5,
                  'F': -5, 'I': -5, 'H': -5, 'K': -5, 'M': -5, 'L': -5,
                  'N': -5, 'Q': -5, 'P': -5, 'S': -5, 'R': -5, 'T': -5,
                  'W': -5, 'V': -5, 'Y': -5, 'X': -5, 'Z': -5},
            'A': {'*': -5, 'A': 5, 'C': -1, 'B': -2, 'E': -1, 'D': -2, 'G': 0,
                  'F': -3, 'I': -1, 'H': -2, 'K': -1, 'M': -1, 'L': -2,
                  'N': -1, 'Q': -1, 'P': -1, 'S': 1, 'R': -2, 'T': 0, 'W': -3,
                  'V': 0, 'Y': -2, 'X': -1, 'Z': -1},
            'C': {'*': -5, 'A': -1, 'C': 13, 'B': -3, 'E': -3, 'D': -4,
                  'G': -3, 'F': -2, 'I': -2, 'H': -3, 'K': -3, 'M': -2,
                  'L': -2, 'N': -2, 'Q': -3, 'P': -4, 'S': -1, 'R': -4,
                  'T': -1, 'W': -5, 'V': -1, 'Y': -3, 'X': -1, 'Z': -3},
            'B': {'*': -5, 'A': -2, 'C': -3, 'B': 6, 'E': 1, 'D': 6, 'G': -1,
                  'F': -4, 'I': -4, 'H': 0, 'K': 0, 'M': -3, 'L': -4, 'N': 5,
                  'Q': 0, 'P': -2, 'S': 0, 'R': -1, 'T': 0, 'W': -5, 'V': -3,
                  'Y': -3, 'X': -1, 'Z': 1},
            'E': {'*': -5, 'A': -1, 'C': -3, 'B': 1, 'E': 6, 'D': 2, 'G': -3,
                  'F': -3, 'I': -4, 'H': 0, 'K': 1, 'M': -2, 'L': -3, 'N': 0,
                  'Q': 2, 'P': -1, 'S': -1, 'R': 0, 'T': -1, 'W': -3, 'V': -3,
                  'Y': -2, 'X': -1, 'Z': 5},
            'D': {'*': -5, 'A': -2, 'C': -4, 'B': 6, 'E': 2, 'D': 8, 'G': -1,
                  'F': -5, 'I': -4, 'H': -1, 'K': -1, 'M': -4, 'L': -4, 'N': 2,
                  'Q': 0, 'P': -1, 'S': 0, 'R': -2, 'T': -1, 'W': -5, 'V': -4,
                  'Y': -3, 'X': -1, 'Z': 1},
            'G': {'*': -5, 'A': 0, 'C': -3, 'B': -1, 'E': -3, 'D': -1, 'G': 8,
                  'F': -4, 'I': -4, 'H': -2, 'K': -2, 'M': -3, 'L': -4, 'N': 0,
                  'Q': -2, 'P': -2, 'S': 0, 'R': -3, 'T': -2, 'W': -3, 'V': -4,
                  'Y': -3, 'X': -1, 'Z': -2},
            'F': {'*': -5, 'A': -3, 'C': -2, 'B': -4, 'E': -3, 'D': -5,
                  'G': -4, 'F': 8, 'I': 0, 'H': -1, 'K': -4, 'M': 0, 'L': 1,
                  'N': -4, 'Q': -4, 'P': -4, 'S': -3, 'R': -3, 'T': -2, 'W': 1,
                  'V': -1, 'Y': 4, 'X': -1, 'Z': -4},
            'I': {'*': -5, 'A': -1, 'C': -2, 'B': -4, 'E': -4, 'D': -4,
                  'G': -4, 'F': 0, 'I': 5, 'H': -4, 'K': -3, 'M': 2, 'L': 2,
                  'N': -3, 'Q': -3, 'P': -3, 'S': -3, 'R': -4, 'T': -1,
                  'W': -3, 'V': 4, 'Y': -1, 'X': -1, 'Z': -3},
            'H': {'*': -5, 'A': -2, 'C': -3, 'B': 0, 'E': 0, 'D': -1, 'G': -2,
                  'F': -1, 'I': -4, 'H': 10, 'K': 0, 'M': -1, 'L': -3, 'N': 1,
                  'Q': 1, 'P': -2, 'S': -1, 'R': 0, 'T': -2, 'W': -3, 'V': -4,
                  'Y': 2, 'X': -1, 'Z': 0},
            'K': {'*': -5, 'A': -1, 'C': -3, 'B': 0, 'E': 1, 'D': -1, 'G': -2,
                  'F': -4, 'I': -3, 'H': 0, 'K': 6, 'M': -2, 'L': -3, 'N': 0,
                  'Q': 2, 'P': -1, 'S': 0, 'R': 3, 'T': -1, 'W': -3, 'V': -3,
                  'Y': -2, 'X': -1, 'Z': 1},
            'M': {'*': -5, 'A': -1, 'C': -2, 'B': -3, 'E': -2, 'D': -4,
                  'G': -3, 'F': 0, 'I': 2, 'H': -1, 'K': -2, 'M': 7, 'L': 3,
                  'N': -2, 'Q': 0, 'P': -3, 'S': -2, 'R': -2, 'T': -1, 'W': -1,
                  'V': 1, 'Y': 0, 'X': -1, 'Z': -1},
            'L': {'*': -5, 'A': -2, 'C': -2, 'B': -4, 'E': -3, 'D': -4,
                  'G': -4, 'F': 1, 'I': 2, 'H': -3, 'K': -3, 'M': 3, 'L': 5,
                  'N': -4, 'Q': -2, 'P': -4, 'S': -3, 'R': -3, 'T': -1,
                  'W': -2, 'V': 1, 'Y': -1, 'X': -1, 'Z': -3},
            'N': {'*': -5, 'A': -1, 'C': -2, 'B': 5, 'E': 0, 'D': 2, 'G': 0,
                  'F': -4, 'I': -3, 'H': 1, 'K': 0, 'M': -2, 'L': -4, 'N': 7,
                  'Q': 0, 'P': -2, 'S': 1, 'R': -1, 'T': 0, 'W': -4, 'V': -3,
                  'Y': -2, 'X': -1, 'Z': 0},
            'Q': {'*': -5, 'A': -1, 'C': -3, 'B': 0, 'E': 2, 'D': 0, 'G': -2,
                  'F': -4, 'I': -3, 'H': 1, 'K': 2, 'M': 0, 'L': -2, 'N': 0,
                  'Q': 7, 'P': -1, 'S': 0, 'R': 1, 'T': -1, 'W': -1, 'V': -3,
                  'Y': -1, 'X': -1, 'Z': 4},
            'P': {'*': -5, 'A': -1, 'C': -4, 'B': -2, 'E': -1, 'D': -1,
                  'G': -2, 'F': -4, 'I': -3, 'H': -2, 'K': -1, 'M': -3,
                  'L': -4, 'N': -2, 'Q': -1, 'P': 10, 'S': -1, 'R': -3,
                  'T': -1, 'W': -4, 'V': -3, 'Y': -3, 'X': -1, 'Z': -1},
            'S': {'*': -5, 'A': 1, 'C': -1, 'B': 0, 'E': -1, 'D': 0, 'G': 0,
                  'F': -3, 'I': -3, 'H': -1, 'K': 0, 'M': -2, 'L': -3, 'N': 1,
                  'Q': 0, 'P': -1, 'S': 5, 'R': -1, 'T': 2, 'W': -4, 'V': -2,
                  'Y': -2, 'X': -1, 'Z': 0},
            'R': {'*': -5, 'A': -2, 'C': -4, 'B': -1, 'E': 0, 'D': -2, 'G': -3,
                  'F': -3, 'I': -4, 'H': 0, 'K': 3, 'M': -2, 'L': -3, 'N': -1,
                  'Q': 1, 'P': -3, 'S': -1, 'R': 7, 'T': -1, 'W': -3, 'V': -3,
                  'Y': -1, 'X': -1, 'Z': 0},
            'T': {'*': -5, 'A': 0, 'C': -1, 'B': 0, 'E': -1, 'D': -1, 'G': -2,
                  'F': -2, 'I': -1, 'H': -2, 'K': -1, 'M': -1, 'L': -1, 'N': 0,
                  'Q': -1, 'P': -1, 'S': 2, 'R': -1, 'T': 5, 'W': -3, 'V': 0,
                  'Y': -2, 'X': -1, 'Z': -1},
            'W': {'*': -5, 'A': -3, 'C': -5, 'B': -5, 'E': -3, 'D': -5,
                  'G': -3, 'F': 1, 'I': -3, 'H': -3, 'K': -3, 'M': -1, 'L': -2,
                  'N': -4, 'Q': -1, 'P': -4, 'S': -4, 'R': -3, 'T': -3,
                  'W': 15, 'V': -3, 'Y': 2, 'X': -1, 'Z': -2},
            'V': {'*': -5, 'A': 0, 'C': -1, 'B': -3, 'E': -3, 'D': -4, 'G': -4,
                  'F': -1, 'I': 4, 'H': -4, 'K': -3, 'M': 1, 'L': 1, 'N': -3,
                  'Q': -3, 'P': -3, 'S': -2, 'R': -3, 'T': 0, 'W': -3, 'V': 5,
                  'Y': -1, 'X': -1, 'Z': -3},
            'Y': {'*': -5, 'A': -2, 'C': -3, 'B': -3, 'E': -2, 'D': -3,
                  'G': -3, 'F': 4, 'I': -1, 'H': 2, 'K': -2, 'M': 0, 'L': -1,
                  'N': -2, 'Q': -1, 'P': -3, 'S': -2, 'R': -1, 'T': -2, 'W': 2,
                  'V': -1, 'Y': 8, 'X': -1, 'Z': -2},
            'X': {'*': -5, 'A': -1, 'C': -1, 'B': -1, 'E': -1, 'D': -1,
                  'G': -1, 'F': -1, 'I': -1, 'H': -1, 'K': -1, 'M': -1,
                  'L': -1, 'N': -1, 'Q': -1, 'P': -1, 'S': -1, 'R': -1,
                  'T': -1, 'W': -1, 'V': -1, 'Y': -1, 'X': -1, 'Z': -1},
            'Z': {'*': -5, 'A': -1, 'C': -3, 'B': 1, 'E': 5, 'D': 1, 'G': -2,
                  'F': -4, 'I': -3, 'H': 0, 'K': 1, 'M': -1, 'L': -3, 'N': 0,
                  'Q': 4, 'P': -1, 'S': 0, 'R': 0, 'T': -1, 'W': -2, 'V': -3,
                  'Y': -2, 'X': -1, 'Z': 5}}


    def get_blosum50(self):
        return self.blosum50

    def create_unity_sequence_matrix(self):
        charset = self.create_charset_string()
        lcharset = list(charset)
        dictchars2D = {}

        for char_column_index, char_column in enumerate(lcharset):
            dictcharsRow = {}

            for char_row_index, char_row in enumerate(lcharset):

                final_item = None
                if char_column_index == char_row_index:
                    dictcharsRow[char_row] = 0

                else:
                    dictcharsRow[char_row] = 1

            dictchars2D[char_column] = dictcharsRow

        self._unity_sequence_matrix = dictchars2D
        return dictchars2D


    def create_charset_string(self):
        # this is not representing full utf-8 charset
        final_charset = string.printable+"üÜöÖäÄ"
        final_charset = final_charset.replace('@','')
        return final_charset

    @classproperty
    def degenerate_map(cls):
        #return {"X": set("AB")}
        return {}

    @classproperty
    def nondegenerate_chars(cls):
        cs = cls.create_charset_string(cls)
        return set(cs)


    @classproperty
    def definite_chars(cls):
        cs = cls.create_charset_string(cls)
        return set(cs)



    @classproperty
    def default_gap_char(cls):
        # return '¦'
        return '@'

    @classproperty
    def gap_chars(cls):
        # return set('¦')
        return set('@')