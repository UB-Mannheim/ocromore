
from configuration.configuration_handler import ConfigurationHandler
from akf_corelib.conditional_print import ConditionalPrint
import numpy as np
import re

class VocabularyChecker():


    def __init__(self):
        config_handler = ConfigurationHandler(first_init=False)

        self.config = config_handler.get_config()
        self.cpr = ConditionalPrint(self.config.PRINT_VOCABULARY_CHECKER, self.config.PRINT_EXCEPTION_LEVEL,
                                    self.config.PRINT_WARNING_LEVEL)
        self.dict_lines = []
        self.max_edist = None
        self.suggenstion_verbosity = None
        #self.spellchecker = None
        self.special_chars_borders = "!¦1234567890,)(;.:\"-"

        self.pattern_start = re.compile(r"^["+self.special_chars_borders+"]+")
        self.pattern_trail = re.compile(r"["+self.special_chars_borders+"]+$")
        self.pattern_trail_dash = re.compile(r"[-]$")
        self.pattern_only_normal_chars = re.compile(r"[a-zA-Z]+")


    def _load_doc(self, filename):
        # open the file as read only
        file = open(filename, 'r')
        # read all text
        texts = file.readlines()
        # close the file
        file.close()
        return texts

    def without_special_chars(self, input_text):
        len_text = len(input_text)
        input_text_wo_sc = self.pattern_only_normal_chars.findall(input_text)
        if len(input_text_wo_sc) >= 1:
            len_text_wo_sc = len(input_text_wo_sc[0])
            ratio = len_text_wo_sc / len_text
            return input_text_wo_sc[0], ratio
        else:
            # there are only special characters
            return  input_text, 0

    def get_accumulated_confidence_rate(self, word, word_acc_confs, wildcard_char):

        word_reduced, word_starting_borders, word_trailing_borders, change = self.remove_and_give_borders(word)
        wsplit = list(word)

        if change == False:
            acc_conf = 0
            for i in range(0, len(wsplit)):
                acc_conf += word_acc_confs[i]

            return acc_conf, acc_conf/len(wsplit), False, word_starting_borders, word_trailing_borders, word
        else:
            acc_conf = 0

            len_start = len(word_starting_borders)
            len_trail = len(word_trailing_borders)
            for i in range(len_start,len(wsplit)-len_trail):
                acc_conf += word_acc_confs[i]

            return acc_conf, acc_conf / (len(wsplit)-len_start-len_trail), True, word_starting_borders, word_trailing_borders, word_reduced

    def remove_and_give_borders(self, input_text):

        start_sc_text = ""
        stop_sc_text = ""

        if len(input_text) > 2:


            start_special_chars = self.pattern_start.findall(input_text)
            stop_special_chars = self.pattern_trail.findall(input_text)
            if len(start_special_chars) >= 1:
                start_sc_text = start_special_chars[0]
            if len(stop_special_chars) >= 1:
                stop_sc_text = stop_special_chars[0]

            if start_special_chars == None and stop_special_chars == None:
                return input_text, start_sc_text, stop_sc_text, False
            else:
                input_text_stripped = input_text.strip(self.special_chars_borders)
                return input_text_stripped, start_sc_text, stop_sc_text, True
        else:
            return input_text, start_sc_text, stop_sc_text, False

    def word_trails_with_dash(self,input_text):
        trail_dash_res = self.pattern_trail_dash.findall(input_text)
        if len(trail_dash_res) >= 1:
            return True
        else:
            return False

    def initialize_lines(self, dict_file_path, remove_special_border_chars):
        # add the lines from a dictionary path to dict_lines
        doc = self._load_doc(dict_file_path)
        lines_doc = self._get_lines(doc, remove_special_border_chars)
        self.dict_lines.extend(lines_doc)

    def _get_lines(self, doc, remove_special_border_chars):
        lines_doc = []
        for line in doc:
            if "--------------" in line:
                continue

            line = line.replace('\n', "")

            if remove_special_border_chars:
                # print("lbef",line)
                    line = line.strip(self.special_chars_borders)

                # print("laft",line)

            linelen = len(line)
            if linelen > 2:
                if linelen < self.config.KEYING_RESULT_VC_MIN_VOCAB_WORD_LENGTH:
                    continue # filter out lengths which are shorter than minimum

                if self.config.KEYING_RESULT_VC_DOWNCAST_ALL_CASES:
                    line_low = line.lower()
                    if line_low != line:
                        lines_doc.append(line_low)

                lines_doc.append(line)

        return lines_doc

    def initialize_spellchecker(self):
        try:
            from pysymspell.symspell import SymSpell
            if self.dict_lines == None:
                self.cpr.printw("can't initialize spellchecker, please first call initialize_lines")
                return

            # set paramters
            self.max_edist = self.config.KEYING_RESULT_VC_EDIT_DISTANCE_LEVEL
            self.suggenstion_verbosity = SymSpell.Verbosity.CLOSEST

            # initialize symspell as spellchecker
            sym_spell = SymSpell(self.max_edist)

            # load dictionary to spellchecker
            sym_spell.create_dictionary_by_list(self.dict_lines)
            self.spellchecker = sym_spell
        except:
            print(
                "To use the vocabulary checker you must pull PySymSpell from GitHub in the directory (AWARE: MIT License)"
                "by activate and initalize the submodule (delete the comment symbol: #):\n"
                ".gitmodule at line: 1-3")


    def correct_text_at_certain_indices_only(self, input_text, possible_error_indices):

        replacement_char = "‖"
        return_term, suggestions, first_letter_high = self.correct_text(input_text, suggestion_verbosity = SymSpell.Verbosity.ALL)

        if input_text == return_term:
            return return_term
        #print("asd")

        input_text_array = list(input_text)

        #if "Vortrag" in input_text or len(suggestions)>=2:
        #    print("asd")

        suggestion_number_error_correction_count = []

        num_of_possible_suggestions = 0

        for suggestion in suggestions:
            input_text_array_c = input_text_array[:]  # copy input text array
            sug_array = list(suggestion.term)

            for char_index_it, char_it in enumerate(input_text_array):
                for char_index_sug, char_sug in enumerate(sug_array):

                    if input_text_array_c[char_index_it] == sug_array[char_index_sug]:
                        input_text_array_c[char_index_it] = replacement_char
                        sug_array[char_index_sug] = replacement_char
                        continue
            # print("asd")


            number_of_possible_errors_corrected = 0
            # check if char was sustracted in possible error indices
            for index in possible_error_indices:
                char_to_check = input_text_array_c[index]
                char_previous = input_text_array[index]
                if char_to_check == char_previous:
                    number_of_possible_errors_corrected += 1

            if number_of_possible_errors_corrected >= 1:
                num_of_possible_suggestions += 1

            suggestion_number_error_correction_count.append(number_of_possible_errors_corrected)

        if len(suggestion_number_error_correction_count) <= 0:
            return None

        # if num_of_possible_suggestions >=2:
        #     print("asd")

        best_suggestion_index = np.argmax(suggestion_number_error_correction_count)
        best_suggestion_ecccount = suggestion_number_error_correction_count[best_suggestion_index]
        if best_suggestion_ecccount > 0:
            best_suggestion_value = suggestions[best_suggestion_index].term
            if first_letter_high:
                best_suggestion_value = best_suggestion_value[0].upper() + best_suggestion_value[1:]
            return best_suggestion_value
        else:
            return None


    def correct_text(self, input_text, suggestion_verbosity=None):

        first_letter_high = False
        if self.config.KEYING_RESULT_VC_DOWNCAST_ALL_CASES:
            first_letter = input_text[0]
            first_letter_high = first_letter.islower() == False
        #    input_text = input_text.lower()

        suggestion_verbosity_used = self.suggenstion_verbosity
        if suggestion_verbosity != None:
            suggestion_verbosity_used = suggestion_verbosity

        suggestions = self.spellchecker.lookup(input_text, suggestion_verbosity_used, self.max_edist)

        if len(suggestions) >= 1:
            return_term  = suggestions[0]._term
            if self.config.KEYING_RESULT_VC_DOWNCAST_ALL_CASES and first_letter_high:
                return_term = return_term[0].upper() + return_term[1:]

            return return_term, suggestions, first_letter_high
        else:
            return None, suggestions, first_letter_high

