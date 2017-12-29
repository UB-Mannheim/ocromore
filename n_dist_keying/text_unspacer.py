import difflib
import re
from utils.queues import Ranged_Filo

class TextUnspacer:


    @staticmethod
    def map_spaced_2_spaceless_text(text_spaced, text_spaceless):


        sqmatch = difflib.SequenceMatcher(None, text_spaceless, text_spaced, True)
        mb = sqmatch.get_matching_blocks()


        if "A u" in str(text_spaced):
            print("Aufsichtsrat ")

    @staticmethod
    def unspace_texts(text_list, non_spaced_index = None):

        only_characters = True
        search_range_filo = 1
        size_filo = 3


        for line_index, line in enumerate(text_list):
           for line_cmp_index, line_cmp in enumerate(text_list):

                if line_index is line_cmp_index:
                    continue
                if line is False or line is True or line_cmp is False or line_cmp is True: #todo remove this
                    continue


                text = line.ocr_text_normalized
                text_split = list(text)
                print("Text is ", text)

                # pad up the rest, for fifo clearance
                for i in range(0, size_filo):
                    text_split.append('¦')


                current_chars_filo = Ranged_Filo(size_filo, search_range_filo)

                for index_char, char in enumerate(text_split):
                    current_chars_filo.push(char)
                    middle_items = current_chars_filo.get_middle_items(True, True)
                    if middle_items[current_chars_filo.get_middle_index()] is ' ':
                        print("Index_char:", index_char,"Char: ", char, "Tuple:", middle_items)
                    #if char is ' ':
                      #  print("smth")
                just_stop


    @staticmethod
    def unspace_texts_old(text_list, non_spaced_index = None):

        only_characters = True

        for line_index, line in enumerate(text_list):



            for line_cmp_index, line_cmp in enumerate(text_list):

                if line_index is line_cmp_index:
                    continue
                if line is False or line is True or line_cmp is False or line_cmp is True: #todo remove this
                    continue


                line_text = line.ocr_text_normalized
                line_cmp_text = line_cmp.ocr_text_normalized

                line_text_result = line.ocr_text_normalized
                line_text_cmp_result = line_cmp.ocr_text_normalized

                if "Aufsichtsrat" in str(line_text):
                    print("Aufsichtsrat ")

                if only_characters is True:
                    line_text = re.sub("[^a-zA-ZüÜöÖäÄ\s]+", "¦", line_text)
                    line_cmp_text = re.sub("[^a-zA-ZüÜöÖäÄ\s]+", "¦", line_cmp_text)

                line_text_spaceless = line_text.replace(' ', '')
                line_cmp_text_spaceless = line_cmp_text.replace(' ', '')

                space_mapping_1 = TextUnspacer.map_spaced_2_spaceless_text(line_text, line_text_spaceless)
                space_mapping_2 = TextUnspacer.map_spaced_2_spaceless_text(line_cmp_text, line_cmp_text_spaceless)


                #do comparison here:
                sqmatch = difflib.SequenceMatcher(None, line_text, line_cmp_text, True)
                sqmatch_sl = difflib.SequenceMatcher(None, line_text_spaceless, line_cmp_text_spaceless, True)

                print("Comparing: ", line_text, "||", line_cmp_text,"||------------------------")

                blocks = sqmatch.get_matching_blocks()
                for block in blocks:
                    (str1_starti, str2_starti, match_length) = block
                    str1_substr = line_text[str1_starti:str1_starti + match_length]
                    str2_substr = line_cmp_text[str1_starti:str1_starti + match_length]
                    print("Str1 substr: ", str1_substr)
                    print("Str2 substr: ", str2_substr)

                blocks = sqmatch_sl.get_matching_blocks()
                for block in blocks:
                    (str1_starti, str2_starti, match_length) = block
                    str1_substr = line_text_spaceless[str1_starti:str1_starti + match_length]
                    str2_substr = line_cmp_text_spaceless[str1_starti:str1_starti + match_length]
                    print("Str1 sl substr: ", str1_substr)
                    print("Str2 sl substr: ", str2_substr)

