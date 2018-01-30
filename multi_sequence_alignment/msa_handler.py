from multi_sequence_alignment.msa_algorithm import MultiSequenceAlignment
import numpy as np

class MsaHandler(object):

    @staticmethod
    def compare(item_one, item_two, wildcard_character='¦'):
        sequences1 = [item_one]
        sequences2 = [item_two]

        sSequences1, sSequences2 = MultiSequenceAlignment.msa(sequences1, sequences2)
        """
        for i in range(len(sSequences1)):
            s1 = ''.join(['-' if element == '' else element \
                          for element in sSequences1[i]])
            s2 = ''.join(['-' if element == '' else element \
                          for element in sSequences2[i]])

            print(s1)
            print(s2)
            print()
        """
        s1 = ''.join([wildcard_character if element == '' else element \
                      for element in sSequences1[0]])
        s2 = ''.join([wildcard_character if element == '' else element \
                      for element in sSequences2[0]])

        return s1, s2

    @staticmethod
    def get_same_count(c1, c2, c3):
        same_ctr = 0
        if c1 == c2:
            same_ctr += 1

        if c1 == c3:
            same_ctr += 1

        return same_ctr


    @staticmethod
    def best_of_three_simple(line_1, line_2, line_3, index_best, wildcard_character='¦'):
        list_line_1 = list(line_1)
        list_line_2 = list(line_2)
        list_line_3 = list(line_3)

        accumulated_chars = ""
        for character_index, character_1 in enumerate(list_line_1):
            character_2 = list_line_2[character_index]
            character_3 = list_line_3[character_index]

            clist = [character_1, character_2, character_3]
            sc1 = MsaHandler.get_same_count(character_1, character_2, character_3)
            sc2 = MsaHandler.get_same_count(character_2, character_1, character_3)
            sc3 = MsaHandler.get_same_count(character_3, character_2, character_1)
            maxindices = np.argmax([sc2, sc1, sc3])
            if maxindices == 0:
                accumulated_chars += character_2
            elif maxindices == 1:
                accumulated_chars += character_1
            else:
                accumulated_chars += character_3

        accumulated_chars_stripped = accumulated_chars.replace(wildcard_character, '')

        return accumulated_chars, accumulated_chars_stripped

    @staticmethod
    def fillup_wildcarded_result(line_to_fill, reference_line, wildcard_character='¦'):
        import difflib
        from utils.random import Random

        s = difflib.SequenceMatcher(None, line_to_fill, reference_line)

        mbs = s.get_matching_blocks()

        line_filled = ""
        last_start=0
        transition = 0
        for idx, block in enumerate(mbs):
            (str1_starti, str2_starti, match_length) = block

            str1_substr = line_to_fill[str1_starti:str1_starti + match_length]
            str_1_to_fill = line_to_fill[last_start:str1_starti + match_length]
            last_start = str1_starti + match_length

            str2_substr = reference_line[str2_starti:str2_starti + match_length]
            if match_length > 1 and str2_starti > (transition+str1_starti):
                diff = str2_starti - (transition + str1_starti)
                #diff = str2_starti - (transition + last_start)


                transition += diff
                #line_filled += wildcard_character
                line_filled = Random.append_pad_values(line_filled, diff, wildcard_character)
            line_filled += str_1_to_fill

        # just a  trick to fill up in some cases
        length_diff = len(reference_line) - len(line_filled)
        if length_diff > 0:
            line_filled = Random.append_pad_values(line_filled, length_diff, wildcard_character)

        return line_filled


    @staticmethod
    def get_best_of_three(text_1, text_2, text_3):

        PRINT_RESULTS = True
        # list_one = list('1. Wie funktioniert der Algorithmus')
        # list_two = list('2. Wie funktioniert hier der Algorithmus')  # this is the pivot element
        # list_three = list('3. Wie der Algorithmus')

        #text_1 = "had I expressed the agony I frequentl felt he would have been taught to long for its alleviation"
        #text_2 = "had I sed the agony I fefjuently felt he would have been to long for its alleviafcion"
        #text_3 = "had I expressed tbe agony I frequently felt he would have been taught to long for its alleviation"

        list_one = list(text_1)
        list_two = list(text_2)  # this is the pivot element
        list_three = list(text_3)

        res_one_1, res_two_1 = MsaHandler.compare(list_one, list_two)


        res_two_2, res_three_2 = MsaHandler.compare(list_two, list_three)

        list_res_one_1 = list(res_one_1)
        list_res_two_1 = list(res_two_1)

        list_res_two_2 = list(res_two_2)
        list_res_three_2 = list(res_three_2)

        list_pivot_msa = None
        pivot_msa = None
        if len(list_res_two_1) >= len(list_res_two_2):
        #if len(list_res_two_1) > len(list_res_two_2):
            list_pivot_msa = list_res_two_1
            pivot_msa = res_two_1
        else:
            list_pivot_msa = list_res_two_2
            pivot_msa = res_two_2

        print(len(res_one_1), res_one_1)
        print(len(pivot_msa), pivot_msa)
        print(len(res_three_2), res_three_2)
        #if res_one_1.__contains__("Sitz:") is True:
        #    print("asd")

        res_one_1_filled = MsaHandler.fillup_wildcarded_result(res_one_1, pivot_msa)
        res_three_2_filled = MsaHandler.fillup_wildcarded_result(res_three_2, pivot_msa)

        res_final_1 = res_one_1_filled
        res_final_2 = pivot_msa
        # res_final_3 = res_three_2
        res_final_3 = res_three_2_filled
        """
        res_final_1, holder1 = MsaHandler.compare(list_res_one_1, list_pivot_msa)
        res_final_2 = pivot_msa
        res_final_3, holder2 = MsaHandler.compare(list_res_three_2, list_pivot_msa)
        """
        #j4t
        #rres_final_1, rholder1 = MsaHandler.compare(list_pivot_msa, list_res_one_1)
        #rres_final_2 = pivot_msa
        #rres_final_3, rholder2 = MsaHandler.compare( list_pivot_msa, list_res_three_2)


        best, best_stripped = MsaHandler.best_of_three_simple(res_final_1, res_final_2, res_final_3, 1)  # res two is the best element
        best_stripped_non_multi_whitespace = ' '.join(best_stripped.split())

        if PRINT_RESULTS:
            """
                print("A:", res_one_1)
                print("B:", res_two_2)
                print("C:", res_three_2)
                print("D:", best)
                print("E:", best_stripped)
                print("F:", best_stripped_non_multi_whitespace)
            """
            print("0:", res_one_1)
            print("A:",res_final_1)
            print("B:",res_final_2)
            print("C:",res_final_3)
            print("D:", best)
            print("E:", best_stripped)
            print("F:", best_stripped_non_multi_whitespace)
        return best_stripped_non_multi_whitespace