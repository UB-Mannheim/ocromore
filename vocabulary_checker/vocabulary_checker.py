from pysymspell.symspell import SymSpell
from configuration.configuration_handler import ConfigurationHandler
from utils.conditional_print import ConditionalPrint
import re

class VocabularyChecker():


    def __init__(self):
        config_handler = ConfigurationHandler(first_init=False)

        self.config = config_handler.get_config()
        self.cpr = ConditionalPrint(self.config.PRINT_VOCABULARY_CHECKER, self.config.PRINT_EXCEPTION_LEVEL,
                                    self.config.PRINT_WARNING_LEVEL)
        self.dict_lines = None
        self.max_edist = None
        self.suggenstion_verbosity = None
        self.spellchecker = None
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

    def _border_text_removal(self, input_text):
        print("asd")
        if len(input_text)>2:
            print("asd")

        else:
            return

    def initialize_lines(self, dict_file_path, remove_special_border_chars):
        doc = self._load_doc(dict_file_path)

        lines_doc = []
        for line in doc:
            if "--------------" in line:
                continue

            line = line.replace('\n', "")

            if remove_special_border_chars:
                # print("lbef",line)
                    line = line.strip(self.special_chars_borders)

                # print("laft",line)

            if len(line) > 2:
                if self.config.KEYING_RESULT_VC_DOWNCAST_ALL_CASES:
                    line_low = line.lower()
                    if line_low != line:
                        lines_doc.append(line_low)

                lines_doc.append(line)

        self.dict_lines = lines_doc


    def initialize_spellchecker(self):
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


    def correct_text(self, input_text):


        first_letter_high = False
        if self.config.KEYING_RESULT_VC_DOWNCAST_ALL_CASES:
            first_letter = input_text[0]
            first_letter_high = first_letter.islower() == False
        #    input_text = input_text.lower()
        suggestions = self.spellchecker.lookup(input_text, self.suggenstion_verbosity, self.max_edist)

        if len(suggestions) >= 1:
            return_term  = suggestions[0]._term
            if self.config.KEYING_RESULT_VC_DOWNCAST_ALL_CASES and first_letter_high:
                return_term = return_term[0].upper() + return_term[1:]

            return return_term, suggestions
        else:
            return None, suggestions

