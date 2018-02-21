import numpy as np

class OCRVoter(object):

    @staticmethod
    def get_same_count(c1, c2, c3):
        same_ctr = 0
        if c1 == c2:
            same_ctr += 1

        if c1 == c3:
            same_ctr += 1

        return same_ctr

    @staticmethod
    def get_confidence_count(char1, char2, char3, cconf1, cconf2, cconf3, wildcard_char='¦' ):

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
            SPACE_TRESH = 50.0
            SPACE_PUT_IN_VALUE = 99.0
            otherchar, otherconf = get_other_char(char1, char2, char3, cconf1, cconf2, cconf3)
            #print("otherchar",otherchar,"otherconf",otherconf)
            if otherconf < SPACE_TRESH:
                return 1, SPACE_PUT_IN_VALUE

        elif char1 == wildcard_char and same_ctr ==1:
            # if the confidence of the other character is below that value, space gets the high put in confidence value
            WILDCARD_TRESH = 50.0
            WILDCARD_PUT_IN_VALUE = 99.0
            otherchar, otherconf = get_other_char(char1, char2, char3,cconf1,cconf2,cconf3)
            #print("wctr",WILDCARD_TRESH,"otherconf",otherconf)
            if otherconf < WILDCARD_TRESH:
                return 1, WILDCARD_PUT_IN_VALUE
        elif char1 == wildcard_char and same_ctr ==0:
            pass  # todo maybe cover this case (cause wildcard has no confidence i.e if the two otherchars are very low prob, take wildcard)
        elif char1 == '' and same_ctr == 0:
            pass  # todo maybe cover this case (cause space has no confidence ...

        return same_ctr, cconf_ctr


    @staticmethod
    def vote_best_of_three_simple(text_1, text_2, text_3, index_best, wildcard_character='¦'):
        list_line_1 = list(text_1)
        list_line_2 = list(text_2)
        list_line_3 = list(text_3)

        accumulated_chars = ""
        for character_index, character_1 in enumerate(list_line_1):
            character_2 = list_line_2[character_index]
            character_3 = list_line_3[character_index]

            clist = [character_1, character_2, character_3]
            # get the character which occurs the most
            sc1 = OCRVoter.get_same_count(character_1, character_2, character_3)
            sc2 = OCRVoter.get_same_count(character_2, character_1, character_3)
            sc3 = OCRVoter.get_same_count(character_3, character_2, character_1)
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
    def vote_best_of_three_charconfs(line_1, line_2, line_3, index_best, wildcard_character='¦'):

        def try_obtain_charconf(ccconfs, index, undef_val):
            if index >= len(ccconfs):
                return undef_val # return value given if confidence not defined
            else:
                return ccconfs[index]

        def try_obtain_char(charlist, index):
            if index >= len(charlist):
                return False #j4t means not defined
            else:
                return charlist[index]


        key_confs = 'x_confs'
        print("vote_text1",line_1.textstr)
        print("vote_text2",line_2.textstr)
        print("vote_text3",line_3.textstr)

        chars_line_1 = list(line_1.textstr)
        chars_line_2 = list(line_2.textstr)
        chars_line_3 = list(line_3.textstr)
        cconfs_line_1 = line_1.data[key_confs]
        cconfs_line_2 = line_2.data[key_confs]
        cconfs_line_3 = line_3.data[key_confs]
        maximum_char_number = max(len(chars_line_1),len(chars_line_2),len(chars_line_3))
        if len(chars_line_1)!=len(chars_line_2):
            print("ok!")

        accumulated_chars = ""
        for character_index in range(0, maximum_char_number): # check: is list 1 always best reference?

            character_1 = try_obtain_char(chars_line_1, character_index)
            character_2 = try_obtain_char(chars_line_2, character_index)
            character_3 = try_obtain_char(chars_line_3, character_index)
            charconf_1 = try_obtain_charconf(cconfs_line_1, character_index, 0)
            charconf_2 = try_obtain_charconf(cconfs_line_2, character_index, 0)
            charconf_3 = try_obtain_charconf(cconfs_line_3, character_index, 0)



            clist = [character_1, character_2, character_3]
            # get the character which occurs the most
            sc1, acc_conf_1 = OCRVoter.get_confidence_count(character_1, character_2, character_3, charconf_1, charconf_2, charconf_3)
            sc2, acc_conf_2 = OCRVoter.get_confidence_count(character_2, character_1, character_3, charconf_2, charconf_1, charconf_3)
            sc3, acc_conf_3 = OCRVoter.get_confidence_count(character_3, character_2, character_1, charconf_3, charconf_2, charconf_1)
            maxindices = np.argmax([acc_conf_2, acc_conf_1, acc_conf_3]) # this takes in priorisation in case the chars are same
            if maxindices == 0:
                accumulated_chars += character_2
            elif maxindices == 1:
                accumulated_chars += character_1
            else:
                accumulated_chars += character_3

        accumulated_chars_stripped = accumulated_chars.replace(wildcard_character, '')

        return accumulated_chars, accumulated_chars_stripped