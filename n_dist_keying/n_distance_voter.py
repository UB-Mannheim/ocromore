from n_dist_keying.distance_storage import DistanceStorage
from n_dist_keying.text_comparator import TextComparator
import numpy as np


class NDistanceVoter(object):

    def __init__(self, texts):
        self.d_storage = DistanceStorage()
        self._texts = texts

    def set_texts(self, new_texts):
        self._texts = new_texts

    def get_texts(self):
        return self._texts

    def reset(self):
        self.d_storage = DistanceStorage()
        self._texts = []

    def compare_texts(self, take_longest_on_empty_lines=False, vote_without_spaces=False):
        """
        Compares an array of texts and gives the n_distance vote
        :param texts:
        :return:
        """
        texts_loc = self.get_texts()
        if vote_without_spaces:
            for text_index, text in enumerate(texts_loc):
                texts_loc[text_index] = text.replace(" ","")


        if take_longest_on_empty_lines is True:
            texts = self.get_texts()
            textlens = []
            number_empty = 0
            for text in texts:
                textlens.append(len(text))
                if text.strip(" ") == "":
                    number_empty += 1

            too_less_text = (len(texts)-number_empty) <= 2
            if too_less_text:
                # if too less strings to compare, just take the longest string as result
                selected_index = np.argmax(textlens)
                return selected_index


        # do a text-wise comparison, which calculates a distance between all texts in this set
        for text_index, text in enumerate(texts_loc):
            self.compare_with_other_texts(text_index, text)


        # calculate the distance from each item in set to all others
        for text_index, text in enumerate(texts_loc):
            self.d_storage.calculate_accumulated_distance(text_index)

        # get the index of the item in set, which has the shortest distance to all others
        self.d_storage.calculate_shortest_distance_index()
        shortest_dist_index = self.d_storage.get_shortest_distance_index()
        return shortest_dist_index

    def compare_with_other_texts(self, text_index, text):

        for text_index_cmp, text_cmp in enumerate(self.get_texts()):

            # if line has the same index, continue
            if text_index is text_index_cmp:
                continue

            existing_distance = self.d_storage.fetch_value(text_index, text_index_cmp)

            # if line was already compared, continue
            if existing_distance is not None:
                continue

            distance = self.get_distance(text, text_cmp)
            self.d_storage.store_value(text_index, text_index_cmp, distance)


    def get_distance(self, text1, text2):
        # todo add more possibilities for distance measurement, i.e confidences, edit distance, context weighting
        MODE_DIFFLIB = 'difflib' #best bet
        MODE_NORMED_LEVENSHTEIN = 'normed_levenshtein' # longest alignment normed levenshtein distance
        MODE_SORENSEN = 'sorensen'
        MODE_JACCARD = 'jaccard'
        MODE_HAMMING = 'hamming'
        MODE_MYERS = 'myers' # use myers special difflib sequence matcher
        mode = MODE_DIFFLIB # set your mode here

        # return a fixed negative value if one of the strings is not defined
        if text1 is False and text2 is False or text1 is None and text2 is None:
            return 0

        # One is false and one is not false
        if (text1 is False or text2 is False) or (text1 is None or text2 is None):
            return 1

        dist = 1

        if mode == MODE_DIFFLIB:
            dist = TextComparator.compare_ocr_strings_difflib_seqmatch(text1, text2)

        elif mode == MODE_NORMED_LEVENSHTEIN:
            dist = TextComparator.compare_ocr_strings_levensthein_normed(text1, text2)

        elif mode == MODE_HAMMING:
            dist = TextComparator.compare_ocr_strings_hamming(text1, text2)

        elif mode == MODE_SORENSEN:
            dist = TextComparator.compare_ocr_strings_sorensen(text1, text2)

        elif mode == MODE_JACCARD:
            dist = TextComparator.compare_ocr_strings_jaccard(text1, text2)
        elif mode == MODE_MYERS:
            dist = TextComparator.compare_ocr_strings_myers(text1, text2)

        return dist
