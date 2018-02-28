
import sys
from utils.random import Random
from enum import Enum, unique

@unique
class ColumnFeatures(Enum):

    ONE_CHAR_REST_WILDCARDS  = 1
    ONE_CHAR_REST_WHITESPACE = 2
    ONLY_NONE = 3
    MOSTLY_REFERENCE_CHAR = 4  # reference char is in there one or more times


class SearchSpaceProcessor(object):

    def __init__(self, y_size, x_size, wildcard_character, substitution_character):
        print("init ssp")
        self._y_size = y_size
        self._x_size = x_size
        self._middle_index = Random.find_middle(self._x_size, True)
        self._pre_middle_index = self.get_middle_index() - 1
        self._nex_middle_index = self.get_middle_index() + 1

        self._wildcard_character = wildcard_character
        self._substitution_character = substitution_character
        self.similar_chars = []
        self.similar_chars.append(['o', 'ö'])
        self.similar_chars.append(['1', 'l'])
        self.similar_chars.append(['u', 'ü'])
        self.similar_chars.append(['a', 'ä'])
        self.similar_chars.append([':', ';'])
        self.similar_chars.append(['-', '¬'])

        # just for testing ...
        self.similar_chars.append(['.', ','])
        self.similar_chars.append(['i', 'l']) # 1 l i also possible
        # self.similar_chars.append(['e', 'é'])

    def get_middle_index(self):
        return self._middle_index

    def get_simchars_for_char(self, char):

        for simchars in self.similar_chars:
            if char in simchars:
                return simchars

        return [char]

    def get_pre_middle_index(self):
        return self._pre_middle_index

    def get_nex_middle_index(self):
        return self._nex_middle_index

    def get_wildcard_char(self):
        return self._wildcard_character

    def get_substitution_char(self):
        return self._substitution_character

    def get_y_size(self):
        return self._y_size

    def validate_column_features(self, search_space, x_index, reference_char = None, count_up_similar_references=False):
        counter_whitespaces = 0
        counter_wildcards = 0
        counter_nones = 0
        counter_characters = 0
        counter_reference_char = 0
        otherchar = None
        otherchar_y_index = None
        simchars = None
        if reference_char is not None and count_up_similar_references is True:
            simchars = self.get_simchars_for_char(reference_char)
            if len(simchars) != 1:
                print("evaluate")

        # gather data
        for y_index in range(0, self.get_y_size()):
            row = search_space[y_index]
            column_item = row[x_index]
            if column_item == self.get_wildcard_char():
                counter_wildcards += 1
            elif column_item == ' ':
                counter_whitespaces += 1
            elif column_item == None or column_item == False or column_item == True:
                counter_nones += 1
            else:
                if reference_char is not None:

                    if count_up_similar_references is False and column_item == reference_char:
                        counter_reference_char += 1
                    if count_up_similar_references is True:
                        matching = [s for s in simchars if column_item in s]
                        boolmatch = len(matching) >= 1
                        if boolmatch is True:
                            counter_reference_char += 1

                counter_characters += 1
                otherchar = column_item
                otherchar_y_index = y_index

        # extract features
        features = []

        if counter_nones == self.get_y_size():
            features.append(ColumnFeatures.ONLY_NONE.value)
        elif counter_wildcards == self.get_y_size()-1 and counter_characters == 1:
            features.append((ColumnFeatures.ONE_CHAR_REST_WILDCARDS).value)
        elif counter_whitespaces == self.get_y_size()-1 and counter_characters == 1:
            features.append(ColumnFeatures.ONE_CHAR_REST_WHITESPACE.value)
        elif counter_reference_char == self.get_y_size()-1 and (counter_whitespaces == 1 or counter_wildcards == 1):
            features.append(ColumnFeatures.MOSTLY_REFERENCE_CHAR)

        return features, otherchar, otherchar_y_index

    def shift_from_mid(self, search_space, line_index, to_left, other_substition_char = None):
        if other_substition_char is not None:
            used_substitution_char = other_substition_char
        else:
            used_substitution_char = self.get_substitution_char()

        print("shifting")
        mid_val = search_space[line_index][self.get_middle_index()]
        possible_shifts = [' ', self.get_wildcard_char(), used_substitution_char, None, False, True, 0]
        shifted = False
        if to_left is True:
            if search_space[line_index][self.get_pre_middle_index()] in possible_shifts:
                search_space[line_index][self.get_pre_middle_index()] = mid_val
                search_space[line_index][self.get_middle_index()] = used_substitution_char
                shifted = True
        else:
            if search_space[line_index][self.get_nex_middle_index()] in possible_shifts:
                search_space[line_index][self.get_nex_middle_index()] = mid_val
                search_space[line_index][self.get_middle_index()] = used_substitution_char
                shifted = True

        return search_space, shifted

    def process_search_space(self, search_space, search_space_confs, use_similar_chars):
        processed_space = search_space
        processed_space_confs = search_space_confs
        change_done = False


        # self.output_as_scrollbar(search_space) #todo build this in someday

        mid_column_feats, otherchar_mid, oc_mid_index = self.validate_column_features(search_space, self.get_middle_index())

        if ColumnFeatures.ONE_CHAR_REST_WILDCARDS.value in mid_column_feats \
                or ColumnFeatures.ONE_CHAR_REST_WHITESPACE.value in mid_column_feats:

            pre_column_feats, otherchar_pre, oc_pre_index = self.validate_column_features(search_space, \
                                                                        self.get_pre_middle_index(), otherchar_mid, use_similar_chars)
            nex_column_feats, otherchar_nex, oc_nex_index = self.validate_column_features(search_space, \
                                                                        self.get_nex_middle_index(), otherchar_mid, use_similar_chars)

            shifted = False
            left_right = None
            if ColumnFeatures.MOSTLY_REFERENCE_CHAR in pre_column_feats:
                left_right = True
                processed_space, shifted = self.shift_from_mid(search_space, oc_mid_index, left_right)
            if ColumnFeatures.MOSTLY_REFERENCE_CHAR in nex_column_feats:
                left_right = False
                processed_space, shifted = self.shift_from_mid(search_space, oc_mid_index, left_right)
            if shifted:
                processed_space_confs, shifted_confs = self.shift_from_mid(search_space_confs, oc_mid_index,left_right, 0)
                change_done = True


        return processed_space, processed_space_confs, change_done

    def output_as_scrollbar(self, search_space, active=False):
        if active is False:
            return
        sys.stdout.write(f"Scrollingbar {search_space[1]} \r")
        sys.stdout.flush()