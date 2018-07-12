from utils.conditional_print import ConditionalPrint
from configuration.configuration_handler import ConfigurationHandler
from utils.random import Random
import numpy as np

class TableHandler(object):

    def __init__(self):
        config_handler = ConfigurationHandler(first_init=False)

        self.config = config_handler.get_config()
        self.cpr = ConditionalPrint(self.config.PRINT_TABLE_HANDLER, self.config.PRINT_EXCEPTION_LEVEL,
                                    self.config.PRINT_WARNING_LEVEL)
        self.PRINT_TO_CHECKFILE = False
        # a line starting with these words can't be in a table
        self.filter_start_words = ["Fernruf:", "Vorstand:", "Fernschreiber:",
                                   "von","Gründung:", "Ordnungsnr.", "Ordnungsnr",
                                   "Grundkapital:","Umstellung"]

        #with open("checkfile_tables.txt", "w") as myfile:
         #   myfile.write("----" + "\n")

    def recognize_a_line(self, line):

        if line == None or line == False or line == True or line.textstr == None:
            return False

        whole_text = line.textstr
        self.cpr.print("recognizing line:", whole_text)

        # counters
        counter_special_chars = 0
        counter_alphanumerical_chars = 0
        counter_numbers = 0
        counter_chars = len(whole_text)
        counter_alphabetical = 0
        counter_words = 0
        counters_alphabetical_ratios = []
        counters_wordlengths = []
        counters_numbers = []

        character_index = 0
        # special conditions
        ultimo_is_first_word = False
        first_word_no_table_indicator = False
        starts_with_parenthesis = False
        ends_with_parenthesis = False

        last_xstop = 0
        x_box_sizes = []
        x_gaps = []
        for key_index, key in enumerate(line.word['text']):
            word = line.word['text'][key]
            uid_info = line.word['UID'][key]
            word_xstart = line.data['word_x0'][character_index]
            word_xstop = line.data['word_x1'][character_index]
            word_box_size = word_xstop - word_xstart
            x_box_sizes.append(word_box_size)

            if key_index >= 1:
                x_gap = word_xstop - last_xstop
                x_gaps.append(x_gap)

            #line.data['word_x0']
            if word is None or word == "":
                continue

            if key_index == 0:
                if word in self.filter_start_words:
                    first_word_no_table_indicator = True
                if word.lower() == "ultimo":
                    ultimo_is_first_word = True
                if word[0] == "(":
                    starts_with_parenthesis = True


            if key_index == len(line.word['text'])-1:
                if word[-1] == ")":
                    ends_with_parenthesis = True



            counter_alphabetical_chars_word = 0
            counter_alphanumerical_chars_word = 0
            counter_numbers_word = 0


            counter_words += 1

            word_list = list(word)
            for char in word_list:
                if Random.is_special_character(char):
                    counter_special_chars += 1
                elif Random.is_alphanumerical_character(char):
                    counter_alphanumerical_chars += 1
                    counter_alphanumerical_chars_word += 1
                if char.isdigit():
                    counter_numbers += 1
                    counter_numbers_word += 1

            counter_alphabetical_word = counter_alphanumerical_chars_word - counter_numbers_word
            ratio_alphabetical_word = np.round(counter_alphabetical_word/len(word), 2)
            counters_alphabetical_ratios.append(ratio_alphabetical_word)
            counters_wordlengths.append(len(word))
            counters_numbers.append(counter_numbers_word)
            character_index += len(uid_info)
            last_xstop = word_xstop


        # get number of spaces
        len_whole_unspace = len(whole_text.replace(" ", ""))
        counter_spaces = counter_chars - len_whole_unspace
        # set alphabetical counter
        counter_alphabetical = counter_alphanumerical_chars - counter_numbers


        if counter_chars == 0:
            self.cpr.printw("no chars shouldn't happen, no recognizion")
            return False

        special_chars_ratio = counter_special_chars/ counter_chars
        alphanumerical_chars_ratio = counter_alphanumerical_chars / counter_chars
        alphabetical_ratio = counter_alphabetical / counter_chars
        spaces_ratio = counter_spaces/ counter_chars
        numbers_ratio = counter_numbers / counter_chars


        maximum_x_gap = None
        mean_x_gap = None
        median_x_gap = None

        if len(x_gaps) >= 1:
            maximum_x_gap = max(x_gaps)
            mean_x_gap = np.mean(x_gaps)
            median_x_gap = np.median(x_gaps)

        many_numbers_in_first_word = False
        many_alphabetical_in_middle_words = False
        many_alphabetical_in_last_word = False

        # check some middle and last word conditions
        for counter_index, counter in enumerate(counters_wordlengths):
            if counter_index == 0:
                ctr_numbers = counters_numbers[counter_index]
                numbers_ratio_word = np.round(ctr_numbers/counter,2)
                if numbers_ratio_word > 0.8:
                    many_numbers_in_first_word = True
            elif counter_index == len(counters_wordlengths)-1:
                if counter >= 4:
                    alphabetical_ratio_word = counters_alphabetical_ratios[counter_index]
                    if alphabetical_ratio_word >= 0.75:
                        many_alphabetical_in_last_word = True

            else:
                if counter >= 4:
                    alphabetical_ratio_word = counters_alphabetical_ratios[counter_index]
                    if alphabetical_ratio_word >= 0.75:
                        many_alphabetical_in_middle_words = True



        self.cpr.print("alle cntr:", counter_chars)
        self.cpr.print("spec cntr:", counter_special_chars, "ratio", special_chars_ratio)
        self.cpr.print("alnr cntr:", counter_alphanumerical_chars, "ratio", alphanumerical_chars_ratio)
        self.cpr.print("albt cntr:", counter_alphabetical, "ratio", alphabetical_ratio)
        self.cpr.print("spce cntr:", counter_spaces, "ratio", spaces_ratio)
        self.cpr.print("nmbr cntr:", counter_numbers, "ratio", numbers_ratio)
        self.cpr.print("x_box_sizes", x_box_sizes)
        self.cpr.print("x_gaps", x_gaps)
        self.cpr.print("x_gap_max_size", maximum_x_gap)
        self.cpr.print("x_gaps_mean", mean_x_gap)
        self.cpr.print("x_gaps_median", median_x_gap)

        if "Gewinn nach Vortrag" in whole_text:
            print("")


        if ((alphabetical_ratio < 0.75 and \
            numbers_ratio > 0.2 and \
            counter_chars > 5 and \
            counter_words >= 2) and not \
            (starts_with_parenthesis and ends_with_parenthesis)) or ultimo_is_first_word:

            if first_word_no_table_indicator:
                return False

            if mean_x_gap <= 115:
                return False
            if many_alphabetical_in_last_word:
                return False
            if many_alphabetical_in_middle_words and many_numbers_in_first_word:
                return False


            self.cpr.print("possible entry:", whole_text)

            if self.PRINT_TO_CHECKFILE:
                with open("checkfile_tables.txt", "a") as myfile:
                    myfile.write(whole_text+ "||| max x_gap: " + str(maximum_x_gap)+"||| mean x_gap: " + str(mean_x_gap) \
                             + "||| median x_gap: " + str(median_x_gap)+"\n")

            print("jab")
            return True

        return False