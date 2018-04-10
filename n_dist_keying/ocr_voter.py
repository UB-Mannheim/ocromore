from utils.conditional_print import ConditionalPrint
from utils.queues import SearchSpace
from n_dist_keying.search_space_processor import SearchSpaceProcessor
import numpy as np
import inspect
from utils.conditional_print import ConditionalPrint
from configuration.configuration_handler import ConfigurationHandler

class SpecialChars():
    umlauts_caps = "ÄÜÖ"
    umlauts = umlauts_caps.lower()
    umlaut_increment = 18



class OCRVoter(object):

    def __init__(self):
        config_handler = ConfigurationHandler(first_init=False)
        self.config = config_handler.get_config()
        self.cpr = ConditionalPrint(self.config.PRINT_MSA_HANDLER, self.config.PRINT_EXCEPTION_LEVEL,
                                    self.config.PRINT_WARNING_LEVEL)




    def get_same_count(self, c1, c2, c3):
        same_ctr = 0
        if c1 == c2:
            same_ctr += 1

        if c1 == c3:
            same_ctr += 1

        return same_ctr


    def get_confidence_count(self, char1, char2, char3, cconf1, cconf2, cconf3, wildcard_char='¦' ):

        def get_other_char(char_first, char_sec, char_thrd, co1, co2,co3):
            if char_first != char_sec:
                return char_sec, float(co2)
            elif char_first != char_thrd:
                return char_thrd, float(co3)


        same_ctr = 0
        cconf_ctr = float(cconf1)

        if char1 == char2:
            same_ctr += 1
            cconf_ctr += float(cconf2)
        if char1 == char3:
            same_ctr += 1
            cconf_ctr += float(cconf3)

        # special cases space: ' ', ' ', 'x'
        # wildcard character : '¦', '¦', '¦'

        if char1 == ' ' and same_ctr == 1:
            # if the confidence of the other character is below that value, space gets the high put in confidence value
            return 1, 95.0 #todo j4t

            SPACE_TRESH = 50.0
            SPACE_PUT_IN_VALUE = 99.0
            otherchar, otherconf = get_other_char(char1, char2, char3, cconf1, cconf2, cconf3)
            #print("otherchar",otherchar,"otherconf",otherconf)
            if otherconf < SPACE_TRESH:
                return 1, SPACE_PUT_IN_VALUE

        elif char1 == wildcard_char and same_ctr ==1: #todo: differentiate type of character ??
            # if there is two wildcards and one characters, characters confidence has to be higher than
            # WILDCARD_TRESH to be taken
            WILDCARD_TRESH = 98.5
            return 1, WILDCARD_TRESH
            # if the confidence of the other character is below that value, space gets the high put in confidence value
            WILDCARD_PUT_IN_VALUE = 99.0
            otherchar, otherconf = get_other_char(char1, char2, char3,cconf1,cconf2,cconf3)
            #print("wctr",WILDCARD_TRESH,"otherconf",otherconf)
            if otherconf < WILDCARD_TRESH:
                return 1, WILDCARD_PUT_IN_VALUE
        elif char1 == wildcard_char and same_ctr == 0:
            pass  # todo maybe cover this case (cause wildcard has no confidence i.e if the two otherchars are very low prob, take wildcard)
        elif char1 == '' and same_ctr == 0:
            pass  # todo maybe cover this case (cause space has no confidence ...

        return same_ctr, cconf_ctr



    def vote_best_of_three_simple(self, text_1, text_2, text_3, index_best, wildcard_character='¦'):
        list_line_1 = list(text_1)
        list_line_2 = list(text_2)
        list_line_3 = list(text_3)

        accumulated_chars = ""
        for character_index, character_1 in enumerate(list_line_1):
            character_2 = list_line_2[character_index]
            character_3 = list_line_3[character_index]

            clist = [character_1, character_2, character_3]
            # get the character which occurs the most
            sc1 = self.get_same_count(character_1, character_2, character_3)
            sc2 = self.get_same_count(character_2, character_1, character_3)
            sc3 = self.get_same_count(character_3, character_2, character_1)
            maxindices = np.argmax([sc2, sc1, sc3])
            if maxindices == 0:
                accumulated_chars += character_2
            elif maxindices == 1:
                accumulated_chars += character_1
            else:
                accumulated_chars += character_3

        accumulated_chars_stripped = accumulated_chars.replace(wildcard_character, '')

        return accumulated_chars, accumulated_chars_stripped


    def vote_best_of_three_charconfs(self, line_1, line_2, line_3, index_best, wildcard_character='¦'):
        try:

            def try_obtain_charconf(value, undef_value=0):
                if value is None or value is False or value is True:
                    return undef_value
                return value

            def try_obtain_char(charlist, index):
                if index >= len(charlist):
                    return False #j4t means not defined
                else:
                    return charlist[index]


            key_confs_mapping = 'UID'
            key_confs = 'x_confs'
            key_char = 'calc_char'
            self.cpr.print("vote_text1", line_1.textstr)
            self.cpr.print("vote_text2", line_2.textstr)
            self.cpr.print("vote_text3", line_3.textstr)
            #if "¦¦lt.H" in line_1.textstr:
            #    self.cpr.print("asd")

            maximum_char_number = max(len(line_1.textstr), len(line_2.textstr), len(line_3.textstr))

            accumulated_chars = ""
            for character_index in range(0, maximum_char_number): # check: is list 1 always best reference?

                character_1 = line_1.value(key_char, character_index)
                character_2 = line_2.value(key_char, character_index)
                character_3 = line_3.value(key_char, character_index)

                charconf_1 = try_obtain_charconf(line_1.value(key_confs, character_index, wsval=50.0))
                charconf_2 = try_obtain_charconf(line_2.value(key_confs, character_index, wsval=50.0))
                charconf_3 = try_obtain_charconf(line_3.value(key_confs, character_index, wsval=50.0))

                clist = [character_1, character_2, character_3]
                # get the character which occurs the most
                sc1, acc_conf_1 = self.get_confidence_count(character_1, character_2, character_3, charconf_1, charconf_2, charconf_3)
                sc2, acc_conf_2 = self.get_confidence_count(character_2, character_1, character_3, charconf_2, charconf_1, charconf_3)
                sc3, acc_conf_3 = self.get_confidence_count(character_3, character_2, character_1, charconf_3, charconf_2, charconf_1)
                maxindices = np.argmax([acc_conf_2, acc_conf_1, acc_conf_3]) # this takes in priorisation in case the chars are same
                if maxindices == 0:
                    accumulated_chars += character_2
                elif maxindices == 1:
                    accumulated_chars += character_1
                else:
                    accumulated_chars += character_3

            accumulated_chars_stripped = accumulated_chars.replace(wildcard_character, '')

            return accumulated_chars, accumulated_chars_stripped
        except Exception as ex:
            tr = inspect.trace()

            self.cpr.printex("ocr_voter.py Exception during confidence vote:", ex)
            self.cpr.printex("trace is:", tr)

    def increase_umlaut_confidence(self, chars, charconfs):

        charconfs_adapted = []

        for char_index, char in enumerate(chars):
            if char in SpecialChars.umlauts_caps or char in SpecialChars.umlauts:
                cconf_to_add = charconfs[char_index] + SpecialChars.umlaut_increment
            else:
                cconf_to_add = charconfs[char_index]

            charconfs_adapted.append(cconf_to_add)

        return charconfs_adapted


    def vote_best_of_three_charconfs_searchspaces(self, line_1, line_2, line_3, index_best, wildcard_character='¦'):
        try:

            def try_obtain_charconf(value, undef_value=0):
                if value is None or value is False or value is True:
                    return undef_value
                return value

            def try_obtain_char(charlist, index):
                if index >= len(charlist):
                    return False  # j4t means not defined
                else:
                    return charlist[index]

            key_confs_mapping = 'UID'
            key_confs = 'x_confs'
            key_char = 'calc_char'
            self.cpr.print("vote_text1", line_1.textstr)
            self.cpr.print("vote_text2", line_2.textstr)
            self.cpr.print("vote_text3", line_3.textstr)
            if "1150" in line_1.textstr:
                 self.cpr.print("asd")

            maximum_char_number = max(len(line_1.textstr), len(line_2.textstr), len(line_3.textstr))

            accumulated_chars = ""


            SEARCH_SPACE_Y_SIZE = 3
            SEARCH_SPACE_X_SIZE_OUTER = 7
            SEARCH_SPACE_X_SIZE_INNER = 3
            SEARCH_SPACE_X_SEARCH_RANGE = 1
            SEARCH_SPACE_PROCESSING_SUBSTITUTION_CHAR ='¦'
            SEARCH_SPACE_PROCESSING_USE_SIMILAR_CHARS = True
            SEARCH_RANGE = 1
            PRINT_MATRICES = self.config.PRINT_SEARCH_SPACE_MATRICES

            search_space_processor = SearchSpaceProcessor(SEARCH_SPACE_Y_SIZE, SEARCH_SPACE_X_SIZE_INNER, \
                                                          wildcard_character, SEARCH_SPACE_PROCESSING_SUBSTITUTION_CHAR)

            ssp_chars = SearchSpace(SEARCH_SPACE_Y_SIZE, SEARCH_SPACE_X_SIZE_OUTER, SEARCH_SPACE_X_SEARCH_RANGE, True)
            ssp_confs = SearchSpace(SEARCH_SPACE_Y_SIZE, SEARCH_SPACE_X_SIZE_OUTER, SEARCH_SPACE_X_SEARCH_RANGE, True)

            range_extension = SEARCH_SPACE_X_SIZE_INNER
            for character_index in range(0, maximum_char_number+range_extension+2):  # check: is list 1 always best reference?
                if character_index < maximum_char_number:
                    line_vals = [line_1.value(key_char, character_index), line_2.value(key_char, character_index), \
                                 line_3.value(key_char, character_index)]

                    charconf_1 = try_obtain_charconf(line_1.value(key_confs, character_index, wsval=50.0))
                    charconf_2 = try_obtain_charconf(line_2.value(key_confs, character_index, wsval=50.0))
                    charconf_3 = try_obtain_charconf(line_3.value(key_confs, character_index, wsval=50.0))
                    charconf_vals = [charconf_1, charconf_2, charconf_3]
                else:
                    line_vals = [None, None, None]
                    charconf_vals = [None, None, None]

                ssp_chars.push_column(line_vals)
                ssp_confs.push_column(charconf_vals)

                mid_chars = ssp_chars.get_middle_matrix(PRINT_MATRICES)
                mid_confs = ssp_confs.get_middle_matrix(PRINT_MATRICES)
                mid_chars_processed, mid_confs_processed, change_done = \
                    search_space_processor.process_search_space(mid_chars, mid_confs,SEARCH_SPACE_PROCESSING_USE_SIMILAR_CHARS)
                if change_done is True:
                    ssp_chars.update_middle_matrix(mid_chars_processed)
                    ssp_confs.update_middle_matrix(mid_confs_processed)


                # mind range here
                character_offset = -(SEARCH_SPACE_X_SEARCH_RANGE+1)
                character_1 = ssp_chars.get_value_around_middle(0, character_offset)
                character_2 = ssp_chars.get_value_around_middle(1, character_offset)
                character_3 = ssp_chars.get_value_around_middle(2, character_offset)
                charconf_1 = ssp_confs.get_value_around_middle(0, character_offset)
                charconf_2 = ssp_confs.get_value_around_middle(1, character_offset)
                charconf_3 = ssp_confs.get_value_around_middle(2, character_offset)
                if character_1 is None or character_2 is None or character_3 is None:
                    # self.cpr.print("test")
                    continue
                if self.config.MSA_BEST_INCREASE_UMLAUT_CONFIDENCE:
                    clist = [character_1, character_2, character_3]
                    conflist = [charconf_1, charconf_2, charconf_3]
                    conflist_new = self.increase_umlaut_confidence(clist, conflist)
                    charconf_1 = conflist_new[0]
                    charconf_2 = conflist_new[1]
                    charconf_3 = conflist_new[2]



                # get the character which occurs the most
                sc1, acc_conf_1 = self.get_confidence_count(character_1, character_2, character_3, charconf_1,
                                                                charconf_2, charconf_3)
                sc2, acc_conf_2 = self.get_confidence_count(character_2, character_1, character_3, charconf_2,
                                                                charconf_1, charconf_3)
                sc3, acc_conf_3 = self.get_confidence_count(character_3, character_2, character_1, charconf_3,
                                                                charconf_2, charconf_1)
                maxindices = np.argmax(
                    [acc_conf_2, acc_conf_1, acc_conf_3])  # this takes in priorisation in case the chars are same
                if maxindices == 0:
                    accumulated_chars += character_2
                elif maxindices == 1:
                    accumulated_chars += character_1
                else:
                    accumulated_chars += character_3


            accumulated_chars_stripped = accumulated_chars.replace(wildcard_character, '')

            return accumulated_chars, accumulated_chars_stripped
        except Exception as ex:
            tr = inspect.trace()

            self.cpr.printex("ocr_voter.py Exception during confidence vote", ex)
            self.cpr.printex("trace", tr)
