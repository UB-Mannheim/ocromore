from utils.queues import SearchSpace
from n_dist_keying.search_space_processor import SearchSpaceProcessor
import numpy as np
import inspect
from utils.conditional_print import ConditionalPrint
from utils.random import Random
from configuration.configuration_handler import ConfigurationHandler
from utils.queues import Filo

class SpecialChars():
    # increment some special characters confidence when recognized
    # used if configuration flag MSA_BEST_INCREASE_UMLAUT_CONFIDENCE is active
    umlauts_caps = "ÄÜÖ"
    umlauts = umlauts_caps.lower()
    special_chars = "éáó£"
    umlaut_increment = 18
    special_char_increment = 27

class ConfidenceModifications():
    # scaling factors for confidence values of engines
    # used if configuration flag MSA_BEST_VOTER_SCALE_ENGINE_CONFIDENCES is active
    # 98,02 in 1969
    tesseract_factor = 1.00
    ocropus_factor = 0.96
    abby_factor = 0.83

    # 97,62 in 1969
    #abby_factor = 0.79
    #ocropus_factor = 0.98
    #tesseract_factor = 0.979
    whitespace_push = 100

class OCRVoter(object):

    def __init__(self):
        config_handler = ConfigurationHandler(first_init=False)
        self.config = config_handler.get_config()
        self.cpr = ConditionalPrint(self.config.PRINT_MSA_HANDLER, self.config.PRINT_EXCEPTION_LEVEL,
                                    self.config.PRINT_WARNING_LEVEL)
        self.cpr_vocab_check = ConditionalPrint(self.config.PRINT_VOCABULARY_CHECKER, self.config.PRINT_EXCEPTION_LEVEL,
                                    self.config.PRINT_WARNING_LEVEL)
        self.cpr_sc_predict = ConditionalPrint(self.config.PRINT_SPECIALCHAR_PREDICTOR, self.config.PRINT_EXCEPTION_LEVEL,
                                    self.config.PRINT_WARNING_LEVEL)

        self.filo_last_chars = Filo(250)
        self.predictor = None
        self.use_aufsichtsrat_prediction = False
        self.vocab_checker = None
        self.previous_word_with_seperator = False

    def add_predictor(self, predictor):
        self.predictor = predictor

    def add_vocab_checker(self, vocab_checker):
        self.vocab_checker = vocab_checker

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

        elif char1 == wildcard_char and same_ctr == 1: #todo: differentiate type of character ??
            # if there is two wildcards and one characters, characters confidence has to be higher than
            # WILDCARD_TRESH to be taken

            wildcard_tresh = 98.5
            if self.config.MSA_BEST_CHANGE_VOTING_TRESHS_ON_EMPTY_LINE:
                wildcard_tresh -= 10  # 0:99,19%, 20:99.16%, 10:99.27%

            return 1, wildcard_tresh

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
        accumulated_confs = Filo
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
                if self.config.MSA_BEST_VOTER_DROP_CHARS_BELOW_TRESH == True:
                    tresh = self.config.MSA_BEST_VOTER_DROPPING_TRESH
                    maximum_conf = max(acc_conf_1,acc_conf_2,acc_conf_3)
                    if maximum_conf <tresh:
                        continue


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
            elif char in SpecialChars.special_chars:
                cconf_to_add = charconfs[char_index] + SpecialChars.special_char_increment
            else:
                cconf_to_add = charconfs[char_index]

            charconfs_adapted.append(cconf_to_add)

        return charconfs_adapted

    def vote_best_of_three_charconfs_searchspaces(self, line_1, line_2, line_3, index_best, wildcard_character='¦'):
        try:

            key_confs_mapping = 'UID'
            key_confs = 'x_confs'
            key_char = 'calc_char'
            self.cpr.print("vote_text1", line_1.textstr)
            self.cpr.print("vote_text2", line_2.textstr)
            self.cpr.print("vote_text3", line_3.textstr)
            #if "1150" in line_1.textstr:
            #     self.cpr.print("asd")

            maximum_char_number = max(len(line_1.textstr), len(line_2.textstr), len(line_3.textstr))

            accumulated_chars = ""
            accumulated_confs = Filo(300)

            # search space settings
            SEARCH_SPACE_Y_SIZE = 3
            SEARCH_SPACE_X_SIZE_OUTER = 7
            SEARCH_SPACE_X_SIZE_INNER = 3
            SEARCH_SPACE_X_SEARCH_RANGE = 1
            SEARCH_SPACE_PROCESSING_SUBSTITUTION_CHAR ='¦'
            SEARCH_SPACE_PROCESSING_USE_SIMILAR_CHARS = True
            SEARCH_RANGE = 1
            PRINT_MATRICES = self.config.PRINT_SEARCH_SPACE_MATRICES

            # initialize search space processor and search spaces
            search_space_processor = SearchSpaceProcessor(SEARCH_SPACE_Y_SIZE, SEARCH_SPACE_X_SIZE_INNER, \
                                                          wildcard_character, SEARCH_SPACE_PROCESSING_SUBSTITUTION_CHAR)

            ssp_chars = SearchSpace(SEARCH_SPACE_Y_SIZE, SEARCH_SPACE_X_SIZE_OUTER, SEARCH_SPACE_X_SEARCH_RANGE, True)
            ssp_confs = SearchSpace(SEARCH_SPACE_Y_SIZE, SEARCH_SPACE_X_SIZE_OUTER, SEARCH_SPACE_X_SEARCH_RANGE, True)

            # check if one of the lines is empty for certain settings
            one_line_empty = False
            if self.config.MSA_BEST_VOTER_PUSH_LESS_LINES_WHITESPACE_CONFS or \
                self.config.MSA_BEST_CHANGE_VOTING_TRESHS_ON_EMPTY_LINE:
                one_line_empty = self.check_if_one_line_empty([line_1, line_2, line_3], wildcard_character)

            # loop through the maximum character range of the lines
            range_extension = SEARCH_SPACE_X_SIZE_INNER
            for character_index in range(0, maximum_char_number+range_extension+2):  # check: is list 1 always best reference?

                if character_index < maximum_char_number:
                    # if there is a character within range (no padding char from extension)
                    # get character values and obtain corresponding confidences (from searchspace because they might
                    # be different to normal values because of swapping
                    line_vals = [line_1.value(key_char, character_index), line_2.value(key_char, character_index), \
                                 line_3.value(key_char, character_index)]


                    l_one_is_whitespace = line_vals[0] == ' '
                    l_two_is_whitespace = line_vals[1] == ' '
                    l_thr_is_whitespace = line_vals[2] == ' '

                    charconf_1 = self.try_obtain_charconf_searchspace(line_1.value(key_confs, character_index, wsval=50.0),
                                                     engine_key = line_1.name[0], one_line_empty=one_line_empty,
                                                     is_whitespace=l_one_is_whitespace)
                    charconf_2 = self.try_obtain_charconf_searchspace(line_2.value(key_confs, character_index, wsval=50.0),
                                                     engine_key = line_2.name[0], one_line_empty=one_line_empty,
                                                     is_whitespace=l_two_is_whitespace)
                    charconf_3 = self.try_obtain_charconf_searchspace(line_3.value(key_confs, character_index, wsval=50.0),
                                                     engine_key = line_3.name[0], one_line_empty=one_line_empty,
                                                     is_whitespace=l_thr_is_whitespace)
                    charconf_vals = [charconf_1, charconf_2, charconf_3]
                else:
                    # if the character is within padding range just give none values for characters and confidences
                    line_vals = [None, None, None]
                    charconf_vals = [None, None, None]

                # fill searchspace with the chars and confidences
                ssp_chars.push_column(line_vals)
                ssp_confs.push_column(charconf_vals)

                # update the mid-window of the search space (this is the actual search space processing step)
                mid_chars = ssp_chars.get_middle_matrix(PRINT_MATRICES)
                mid_confs = ssp_confs.get_middle_matrix(PRINT_MATRICES)
                mid_chars_processed, mid_confs_processed, change_done = \
                    search_space_processor.process_search_space(mid_chars, mid_confs,SEARCH_SPACE_PROCESSING_USE_SIMILAR_CHARS)
                if change_done is True:
                    ssp_chars.update_middle_matrix(mid_chars_processed)
                    ssp_confs.update_middle_matrix(mid_confs_processed)

                # extract changed values from search space
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

                # in case umlaut confidence increment is active change charconfs otherwise same charconfs
                charconf_1, charconf_2, charconf_3 = self.increase_umlaut_confidence_searchspace(character_1, character_2, character_3,
                                                                                                 charconf_1, charconf_2, charconf_3)


                # get the previous characters from other lines as string (mainly for predictor)
                filo_content = self.filo_last_chars.get_content_as_string()

                # trigger predicted section for aufsichtsrat predictor
                self.toggle_predictor(filo_content)

                # predict_char if predictor is enabled
                predicted_char = self.predict_char(filo_content)

                # get the character which occurs the most by accumulating confidence scores
                sc1, acc_conf_1 = self.get_confidence_count(character_1, character_2, character_3, charconf_1,
                                                                charconf_2, charconf_3)
                sc2, acc_conf_2 = self.get_confidence_count(character_2, character_1, character_3, charconf_2,
                                                                charconf_1, charconf_3)
                sc3, acc_conf_3 = self.get_confidence_count(character_3, character_2, character_1, charconf_3,
                                                                charconf_2, charconf_1)
                maxindices = np.argmax(
                    [acc_conf_2, acc_conf_1, acc_conf_3])  # this takes in priorisation in case the chars are same

                # drop chars completely if they fall below a certain dropping treshhold and the setting is active
                if self.config.MSA_BEST_VOTER_DROP_CHARS_BELOW_TRESH == True:
                    tresh = self.config.MSA_BEST_VOTER_DROPPING_TRESH
                    maximum_conf = max(acc_conf_1,acc_conf_2,acc_conf_3)
                    if maximum_conf < tresh:
                        continue

                # determine character with the best accumulated confidence
                voted_char = None
                voted_acc_conf = None
                if maxindices == 0:
                    voted_char = character_2
                    voted_acc_conf = acc_conf_2
                elif maxindices == 1:
                    voted_char = character_1
                    voted_acc_conf = acc_conf_1
                else:
                    voted_char = character_3
                    voted_acc_conf = acc_conf_3

                # if predictor is active, check if there is a better char predicted which can replace  voted character
                voted_char = self.maybe_replace_voted_by_predicted_char(voted_char, self.use_aufsichtsrat_prediction,
                                                                        predicted_char, wildcard_character, voted_acc_conf,
                                                                        character_1, character_2, character_3)
                # push the voted char and the accumulated confidence of this char to results
                accumulated_confs.push(voted_acc_conf)
                accumulated_chars += voted_char

                # if the predictor is enabled fill the filo with the voted_char
                self.fill_filo_last_chars(voted_char)

            # do vocabulary related steps, if activated
            accumulated_chars = self.vocabulary_related_corrections(accumulated_chars, wildcard_character,
                                                                    accumulated_confs)

            # remove the wilcard characters and return result
            accumulated_chars_stripped = accumulated_chars.replace(wildcard_character, '')
            return accumulated_chars, accumulated_chars_stripped

        except Exception as ex:
            tr = inspect.trace()

            self.cpr.printex("ocr_voter.py Exception during confidence vote", ex)
            self.cpr.printex("trace", tr)

    def vocabulary_related_corrections(self, accumulated_chars, wildcard_character, accumulated_confs):

        if self.config.KEYING_RESULT_VOCABULARY_CORRECTION_VOTE:
            accumulated_chars_final = ""
            acc_split = accumulated_chars.split()
            len_split = len(acc_split)

            for word_index, word in enumerate(acc_split):

                if self.config.KEYING_RESULT_VC_IGNORE_SEPERATE_WRITING_CORRECTION:
                    if word_index == len_split - 1 and word.replace(wildcard_character, "").endswith('-'):
                        self.previous_word_with_seperator = True
                        accumulated_chars_final += word + " "
                        continue
                    if word_index == 0:
                        if self.previous_word_with_seperator is True:
                            self.previous_word_with_seperator = False
                            accumulated_chars_final += word + " "
                            continue

                acc_confs_word = accumulated_confs.pop_multi(len(word))
                acc_conf, rate, change, word_starting_borders, word_trailing_borders, word_reduced = \
                    self.vocab_checker.get_accumulated_confidence_rate(word, acc_confs_word, wildcard_character)
                self.cpr_vocab_check.print("w:", word, "wr:", word_reduced, "accr:", acc_conf, "rate", rate)

                # don't correct words below min vocab length ( mind that special chars in dict are toggled)
                check_len = len(word)
                if self.config.KEYING_RESULT_VC_DICT_REMOVE_SPECIAL_BORDER_CHARS:
                    check_len = len(word_reduced)
                if check_len < self.config.KEYING_RESULT_VC_MIN_VOCAB_WORD_LENGTH:
                    accumulated_chars_final += word + " "
                    continue

                if self.config.KEYING_RESULT_VC_CORRECT_ONLY_ERRONOUS_CHARS:
                    swappable_char_indices = []

                    acc_confs_used = None
                    word_used = None

                    if self.config.KEYING_RESULT_VC_CORRECT_ERRONOUS_SPECIAL_CHARS:
                        # use the full length confidences array including trailing and leading special characters
                        acc_confs_used = acc_confs_word
                        word_used = word
                    else:
                        # don't use trailing and starting special characters if no special chars needed
                        acc_confs_used = acc_confs_word[len(word_starting_borders):(
                                len(acc_confs_word) - len(word_trailing_borders))]
                        word_used = word_reduced

                    for conf_index, conf in enumerate(acc_confs_used):
                        if self.config.KEYING_RESULT_VC_CORRECT_ERRONOUS_SPECIAL_CHARS:
                            if conf <= 250:
                                character_related = word_used[conf_index]
                                is_special_char = Random.is_special_character(character_related)
                                if is_special_char and character_related != wildcard_character:
                                    # only swap special character indices
                                    swappable_char_indices.append(conf_index)
                        else:
                            if conf <= 215:
                                swappable_char_indices.append(conf_index)

                    if len(swappable_char_indices) >= 1:
                        word_reduced_correct = self.vocab_checker.correct_text_at_certain_indices_only(word_used,
                                                                                                       swappable_char_indices)
                        if word_reduced_correct != None:
                            word_correct_withtrails = None

                            if self.config.KEYING_RESULT_VC_CORRECT_ERRONOUS_SPECIAL_CHARS:
                                if Random.has_special_character(word_reduced_correct):
                                    # if special character was replaced with special character
                                    word_correct_withtrails = word_reduced_correct
                                else:
                                    # if special character was replaced by alphanumerical character
                                    word_correct_withtrails = word
                            else:
                                word_correct_withtrails = word_starting_borders + word_reduced_correct + word_trailing_borders

                            # only print the changed results
                            if word != word_correct_withtrails:
                                self.cpr_vocab_check.print("w:", word, "wc:", word_correct_withtrails,
                                                           "accr:", acc_conf, "rate", rate)

                            accumulated_chars_final += word_correct_withtrails + " "
                        else:
                            accumulated_chars_final += word + " "
                    else:
                        accumulated_chars_final += word + " "

                    continue

                if rate < self.config.KEYING_RESULT_VOCABULARY_CORRECTION_VOTE_TRESH \
                        and len(word_reduced) > 2:
                    # if the rate drops below tresh, try to fetch vocab entry
                    word_reduced_correct, suggestions, flh = self.vocab_checker.correct_text(word_reduced)
                    if word_reduced_correct != None and word_reduced_correct != word_reduced:

                        word_correct_withtrails = word_starting_borders + word_reduced_correct + word_trailing_borders

                        self.cpr_vocab_check.print("w:", word, "wc:", word_correct_withtrails, "accr:", acc_conf, "rate", rate)

                        accumulated_chars_final += word_correct_withtrails + " "
                    else:
                        accumulated_chars_final += word + " "
                else:
                    accumulated_chars_final += word + " "

            accumulated_chars = accumulated_chars_final

        return accumulated_chars

    def try_obtain_charconf_searchspace(self, value, undef_value=0, engine_key=None, one_line_empty=False,
                                        is_whitespace=False):
        if value is None or value is False or value is True:
            return undef_value

        returnvalue = value

        if self.config.MSA_BEST_VOTER_SCALE_ENGINE_CONFIDENCES and engine_key is not None:
            if engine_key == 'Abbyy':
                returnvalue = ConfidenceModifications.abby_factor * value
            elif engine_key == 'Tess':
                returnvalue = ConfidenceModifications.tesseract_factor * value

            elif engine_key == 'Ocro':
                returnvalue = ConfidenceModifications.ocropus_factor * value

        if self.config.MSA_BEST_VOTER_PUSH_LESS_LINES_WHITESPACE_CONFS and one_line_empty \
                and is_whitespace:
            returnvalue += ConfidenceModifications.whitespace_push

        return returnvalue

    def check_if_one_line_empty(self, lines, wildcard_character):
        for line in lines:
            text_wo_wildcards = line.textstr.replace(wildcard_character, '')
            if text_wo_wildcards == "":
                return True


    def toggle_predictor(self, filo_content):
        if self.config.PREDICTOR_AUFSICHTSRAT_ENABLED:
            if "Aufsichtsrat" in filo_content:
                self.use_aufsichtsrat_prediction = True
            if "Gründung:" in filo_content:
                self.use_aufsichtsrat_prediction = False

    def predict_char(self, filo_content):
        predicted_char = None
        if self.use_aufsichtsrat_prediction:
            if len(filo_content) >= 19: # if filo_content bigger than one prediction chunk
                len_aufsichtsrat = 19
                predicted_char = self.predictor.predict_next_aufsichtsrat_chars(len_aufsichtsrat, filo_content)
                # print("filo", filo_content,"predict:", predicted_char)
                # print("dd")
        return predicted_char

    def fill_filo_last_chars(self, voted_char):
        """
        fill filo for predictor usage with voted_char some additional chars around this char
        :param voted_char:
        :return:
        """

        if self.config.PREDICTOR_AUFSICHTSRAT_ENABLED:
            # create pre semi-tokenized input strings in the filos from the voted characters for prediction
            if voted_char == ' ':
                # the models usally use the 'ƿ' char in substitution for spaces
                self.filo_last_chars.push(' ', filterchar='¦')
                self.filo_last_chars.push('ƿ', filterchar='¦')
                self.filo_last_chars.push(' ', filterchar='¦')
            elif Random.is_special_character(voted_char):
                self.filo_last_chars.push(' ', filterchar='¦')
                self.filo_last_chars.push(voted_char, filterchar='¦')
                self.filo_last_chars.push(' ', filterchar='¦')

            else:
                self.filo_last_chars.push(voted_char, filterchar='¦')

    def increase_umlaut_confidence_searchspace(self, character_1, character_2, character_3,
                                               charconf_1, charconf_2, charconf_3):

        if self.config.MSA_BEST_SEARCHSPACE_INCREASE_UMLAUT_CONFIDENCE:
            clist = [character_1, character_2, character_3]
            conflist = [charconf_1, charconf_2, charconf_3]
            conflist_new = self.increase_umlaut_confidence(clist, conflist)
            charconf_1 = conflist_new[0]
            charconf_2 = conflist_new[1]
            charconf_3 = conflist_new[2]
            return charconf_1, charconf_2, charconf_3
        return charconf_1, charconf_2, charconf_3

    def maybe_replace_voted_by_predicted_char(self, voted_char, aufsichtsrat_prediction_toggled, predicted_char, \
                                              wildcard_character, voted_acc_conf, character_1, character_2, character_3):
        if aufsichtsrat_prediction_toggled:
            if Random.is_special_character(predicted_char):
                one_char_sc = Random.is_special_character(character_1) \
                              or Random.is_special_character(character_2) or Random.is_special_character(
                    character_3)
                voted_char_sc = Random.is_special_character(voted_char)

                if predicted_char != voted_char and (
                        one_char_sc or voted_char_sc) and voted_char != wildcard_character:
                    # print("FiloContent:", filo_content)
                    self.cpr_sc_predict.print("pc:", predicted_char, "vc:", voted_char, "vc_acc", voted_acc_conf)
                    if voted_acc_conf <= 90.0:
                        if voted_char != '\f':  # don't swap formfeeds, they don't get predicted at all
                            self.cpr_sc_predict.print("swap")
                            voted_char = predicted_char

        return voted_char