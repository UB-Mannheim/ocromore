
import sys
from utils.random import Random
from enum import Enum, unique
from utils.conditional_print import ConditionalPrint
from configuration.configuration_handler import ConfigurationHandler

@unique
class ColumnFeatures(Enum):  # todo this can be normal class

    ONE_CHAR_REST_WILDCARDS = 1
    ONE_CHAR_REST_WHITESPACE = 2
    ONLY_NONE = 3
    MOSTLY_REFERENCE_CHAR = 4  # reference char is in there one or more times
    ONLY_WHITESPACE = 5
    ONLY_WILDCARD = 6
    ONE_CHAR_REST_WHITESPACE_OR_WILDCARDS = 7
    ONLY_WHITESPACE_OR_WILDCARD = 8
    CONTAINS_REFERENCE_CHAR = 9


class SearchSpaceProcessor(object):

    def __init__(self, y_size, x_size, wildcard_character, substitution_character):
        self._y_size = y_size
        self._x_size = x_size
        self._middle_index = Random.find_middle(self._x_size, True)
        self._pre_middle_index = self.get_middle_index() - 1
        self._nex_middle_index = self.get_middle_index() + 1

        self._wildcard_character = wildcard_character
        self._substitution_character = substitution_character
        self.similar_chars = []
        self.similar_chars.append(['o', 'ö'])
        self.similar_chars.append(['<', 'o']) # untested is this really better?
        self.similar_chars.append(['O', 'Ö'])
        self.similar_chars.append(['0', 'O','9'])
        self.similar_chars.append(['d', 'ö'])
        #self.similar_chars.append(['1', 'l'])
        self.similar_chars.append(['l', 'j', '1'])
        self.similar_chars.append(['I', 'l'])
        self.similar_chars.append(['u', 'ü'])
        self.similar_chars.append(['U', 'Ü','O'])
        self.similar_chars.append(['a', 'ä'])
        self.similar_chars.append(['A', 'Ä'])
        self.similar_chars.append([':', ';'])
        self.similar_chars.append(['-', '¬'])
        self.similar_chars.append(['"', "'"])
        self.similar_chars.append(['C', "G","c"])
        # just for testing ...
        self.similar_chars.append(['.', ','])
        self.similar_chars.append(['v', 'V'])
        self.similar_chars.append(['i', 'l', 't', '1', '.']) # 1 l i also possible
        self.similar_chars.append(['r', 'n'])
        self.similar_chars.append(['%', 'm'])
        self.similar_chars.append(['&', 'é'])
        self.similar_chars.append(['e', 'é'])

        config_handler = ConfigurationHandler(first_init=False)
        self._config = config_handler.get_config()
        self._cpr = ConditionalPrint(self._config.PRINT_SEARCH_SPACE_PROCESSOR, self._config.PRINT_EXCEPTION_LEVEL,
                                     self._config.PRINT_WARNING_LEVEL)


    def get_middle_index(self):
        return self._middle_index

    def get_simchars_for_char(self, char): # todo similar chars for each char could be preprocessed once at start
        simchars_return_array = []

        for simchars in self.similar_chars:
            if char in simchars:
                simchars_return_array.extend(simchars)

        if len(simchars_return_array) >= 1:
            return simchars_return_array

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
                self._cpr.print("evaluate")

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
        counter_whitespace_and_wildcards =  counter_whitespaces + counter_wildcards

        if counter_nones == self.get_y_size():
            features.append(ColumnFeatures.ONLY_NONE.value)
        if counter_wildcards == self.get_y_size()-1 and counter_characters == 1:
            features.append((ColumnFeatures.ONE_CHAR_REST_WILDCARDS).value)
        if counter_whitespaces == self.get_y_size()-1 and counter_characters == 1:
            features.append(ColumnFeatures.ONE_CHAR_REST_WHITESPACE.value)
        if counter_whitespace_and_wildcards == self.get_y_size()-1 and counter_characters == 1:
            features.append(ColumnFeatures.ONE_CHAR_REST_WHITESPACE_OR_WILDCARDS.value)
        if counter_reference_char == self.get_y_size()-1 and (counter_whitespaces == 1 or counter_wildcards == 1):
            features.append(ColumnFeatures.MOSTLY_REFERENCE_CHAR.value)
        if counter_whitespaces == self.get_y_size():
            features.append(ColumnFeatures.ONLY_WHITESPACE.value)
        if counter_reference_char == self.get_y_size():
            features.append(ColumnFeatures.ONLY_WILDCARD.value)
        if counter_whitespace_and_wildcards == self.get_y_size():
            features.append(ColumnFeatures.ONLY_WHITESPACE_OR_WILDCARD.value)
        if counter_reference_char >= 1:
            features.append(ColumnFeatures.CONTAINS_REFERENCE_CHAR.value)


        return features, otherchar, otherchar_y_index

    def shift_from_mid(self, search_space, line_index, to_left, other_substition_char = None):
        if other_substition_char is not None:
            used_substitution_char = other_substition_char
        else:
            used_substitution_char = self.get_substitution_char()

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

    def shift_from_to(self, search_space, y_index, x_from, x_to, other_substition_char = None):

        if other_substition_char is not None:
            used_substitution_char = other_substition_char
        else:
            used_substitution_char = self.get_substitution_char()

        possible_shifts = [' ', self.get_wildcard_char(), used_substitution_char, None, False, True, 0]
        swap_val = search_space[y_index][x_from]

        shifted = False

        if search_space[y_index][x_to] in possible_shifts:
            search_space[y_index][x_to] = swap_val
            search_space[y_index][x_from] = used_substitution_char
            shifted = True

        return search_space, shifted

    def set_space_to_value(self, search_space, y_index, x_index, used_subsitution_value=None):

        if used_subsitution_value is not None:
            used_substitution_char = used_subsitution_value
        else:
            used_substitution_char = self.get_substitution_char()

        search_space[y_index][x_index] = used_substitution_char

        shifted = True



        return search_space, shifted

    def process_search_space(self, search_space, search_space_confs, use_similar_chars):
        processed_space = search_space
        processed_space_confs = search_space_confs
        change_done = False


        # self.output_as_scrollbar(search_space) #todo build this in someday

        mid_column_feats, otherchar_mid, oc_mid_index = self.validate_column_features(search_space, self.get_middle_index())

        if self._config.MSA_BEST_SEARCHSPACE_MITIGATE_SPACE_HOPS:
            # some char 'hopped' over a whitespace, get the characters back together

            if ColumnFeatures.ONLY_WHITESPACE_OR_WILDCARD.value in mid_column_feats:

                pre_column_feats, otherchar_pre, oc_pre_index = self.validate_column_features(search_space, \
                                                                            self.get_pre_middle_index(), reference_char=None)
                nex_column_feats, otherchar_nex, oc_nex_index = self.validate_column_features(search_space, \
                                                                            self.get_nex_middle_index(), reference_char=None)
                if ColumnFeatures.ONE_CHAR_REST_WHITESPACE_OR_WILDCARDS.value in pre_column_feats and \
                    ColumnFeatures.ONE_CHAR_REST_WHITESPACE_OR_WILDCARDS.value in nex_column_feats:

                    if otherchar_nex == otherchar_pre and \
                        oc_pre_index != oc_nex_index:

                        processed_space, shifted_longtrans = self.shift_from_to(search_space, oc_pre_index, 0, 2)

                        if shifted_longtrans is True:

                            processed_space_confs, shifted_confs_longtrangs = self.shift_from_to(search_space_confs, oc_pre_index, 0 , 2, 0)
                            change_done = True

                        if change_done:
                            search_space = processed_space
                            search_space_confs = processed_space_confs



        if ColumnFeatures.ONE_CHAR_REST_WILDCARDS.value in mid_column_feats \
                or ColumnFeatures.ONE_CHAR_REST_WHITESPACE.value in mid_column_feats \
                    or ColumnFeatures.ONE_CHAR_REST_WHITESPACE_OR_WILDCARDS.value in mid_column_feats:

            #if ColumnFeatures.ONE_CHAR_REST_WHITESPACE_OR_WILDCARDS.value in mid_column_feats:
            #if otherchar_mid == "l":
            #    self._cpr.print("beep!")

            pre_column_feats, otherchar_pre, oc_pre_index = self.validate_column_features(search_space, \
                                                                        self.get_pre_middle_index(), otherchar_mid, use_similar_chars)
            nex_column_feats, otherchar_nex, oc_nex_index = self.validate_column_features(search_space, \
                                                                        self.get_nex_middle_index(), otherchar_mid, use_similar_chars)

            shifted = False
            left_right = None
            if ColumnFeatures.MOSTLY_REFERENCE_CHAR.value in pre_column_feats\
                    or (ColumnFeatures.CONTAINS_REFERENCE_CHAR.value in pre_column_feats
                        and ColumnFeatures.ONE_CHAR_REST_WHITESPACE_OR_WILDCARDS.value in pre_column_feats):

                left_right = True
                processed_space, shifted = self.shift_from_mid(search_space, oc_mid_index, left_right)
            if ColumnFeatures.MOSTLY_REFERENCE_CHAR.value in nex_column_feats \
                    or (ColumnFeatures.CONTAINS_REFERENCE_CHAR.value in nex_column_feats
                        and ColumnFeatures.ONE_CHAR_REST_WHITESPACE_OR_WILDCARDS.value in nex_column_feats):
                left_right = False
                processed_space, shifted = self.shift_from_mid(search_space, oc_mid_index, left_right)
            if shifted:

                if self._config.MSA_BEST_SEARCHSPACE_QUOTE_NORMALIZATION  \
                        and (otherchar_mid == "'" or otherchar_mid == '"'):

                    ## this part here merges '' to single ' and corrects the alignment
                    x_middle_index = self.get_middle_index()
                    if left_right is True:
                        delete_index = x_middle_index + 1
                        shift_index =  x_middle_index - 1
                    else:
                        delete_index = x_middle_index - 1
                        shift_index = x_middle_index + 1

                    if otherchar_mid == "'":
                        processed_space, shiftedD1 = self.set_space_to_value(search_space,oc_mid_index, shift_index,'"')
                        processed_space, shiftedD2 = self.set_space_to_value(processed_space,oc_mid_index, delete_index)
                        search_space_confs, shiftedD3 = self.set_space_to_value(search_space_confs,oc_mid_index, delete_index, used_subsitution_value=0)
                    else:
                        # just push confidences because it was confusion with ' and " should be prioritized
                        search_space_confs, shiftedD3 = self.set_space_to_value(search_space_confs, oc_mid_index,
                                                                                shift_index, used_subsitution_value=1000)

                processed_space_confs, shifted_confs = self.shift_from_mid(search_space_confs, oc_mid_index,left_right, 0)
                change_done = True
        elif ColumnFeatures.ONLY_WHITESPACE.value in mid_column_feats or ColumnFeatures.MOSTLY_REFERENCE_CHAR.value in mid_column_feats:
            # this case checks for 'far-transitions' of similar chars and does them if possible
            pre_column_feats, otherchar_pre, oc_pre_index = self.validate_column_features(search_space, \
                                                                        self.get_pre_middle_index(), otherchar_mid, use_similar_chars)
            nex_column_feats, otherchar_nex, oc_nex_index = self.validate_column_features(search_space, \
                                                                        self.get_nex_middle_index(), otherchar_mid, use_similar_chars)
            reference_char = None
            reference_char_y_index = None
            check_index = None

            pre_is_one_char = False
            nex_is_one_char = False
            if ColumnFeatures.ONE_CHAR_REST_WILDCARDS.value in pre_column_feats:
                reference_char = otherchar_pre
                reference_char_y_index = oc_pre_index

                pre_is_one_char = True
                check_index = self.get_nex_middle_index()
                check_index_from = self.get_pre_middle_index()

            if ColumnFeatures.ONE_CHAR_REST_WILDCARDS.value in nex_column_feats:
                reference_char = otherchar_nex
                reference_char_y_index = oc_nex_index
                nex_is_one_char = True
                check_index = self.get_pre_middle_index()
                check_index_from = self.get_nex_middle_index()
            if (pre_is_one_char is True and nex_is_one_char is False) \
                    or (pre_is_one_char is False and nex_is_one_char is True):

                other_column_feats, otherchar_other, oc_other_index = self.validate_column_features(search_space, \
                                                                                                check_index,
                                                                                                reference_char,
                                                                                                  use_similar_chars)

                #print("search_space", search_space)
                if ColumnFeatures.MOSTLY_REFERENCE_CHAR.value in other_column_feats:
                    processed_space, shifted_longtrans = self.shift_from_to(search_space, reference_char_y_index, \
                                                                  check_index_from, check_index)

                    if shifted_longtrans is True:

                        processed_space_confs, shifted_confs_longtrangs = self.shift_from_to(search_space_confs, \
                                                                      reference_char_y_index, check_index_from, check_index, 0)
                        change_done = True


        return processed_space, processed_space_confs, change_done

    def output_as_scrollbar(self, search_space, active=False):
        if active is False:
            return
        sys.stdout.write(f"Scrollingbar {search_space[1]} \r")
        sys.stdout.flush()