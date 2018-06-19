from multi_sequence_alignment.msa_algorithm import MultiSequenceAlignment
import inspect
from Bio import pairwise2
from n_dist_keying.ocr_voter import OCRVoter
from utils.random import Random
import numpy as np
from utils.typecasts import TypeCasts
from utils.conditional_print import ConditionalPrint
from configuration.configuration_handler import ConfigurationHandler

class GapConfig(object):

    def __init__(self, points_identical_char=2, penalty_non_identical_char=-1.3, penalty_opening_gap=-0.5, penalty_extending_gap=-0.4 ):
        self.points_identical_char = points_identical_char
        self.penalty_non_identical_char = penalty_non_identical_char
        self.penalty_opening_gap = penalty_opening_gap
        self.penalty_extending_gap = penalty_extending_gap

class MsaSimilarities(object):
    similar_but_not_same_penalty = 0.4
    sims = []


    # old style sims setup
    # similarity_1 = "l1j"
    # similarity_1_uclist = TypeCasts.convert_string_to_unicode_list(similarity_1)
    # sims.append(similarity_1_uclist)

    similarities_texts = ["l1j",",;"]

    for sim in similarities_texts:
        sim_uclist = TypeCasts.convert_string_to_unicode_list(sim)
        sims.append(sim_uclist)


class MsaHandler(object):

    def __init__(self, predictor = None):
        config_handler = ConfigurationHandler(first_init=False)
        self.config = config_handler.get_config()
        self.cpr = ConditionalPrint(self.config.PRINT_MSA_HANDLER, self.config.PRINT_EXCEPTION_LEVEL,
                                    self.config.PRINT_WARNING_LEVEL)
        self.ocr_voter = OCRVoter()

        if predictor != None:
            self.predictor = predictor
            self.ocr_voter.add_predictor(self.predictor)

        self.vocab_checker = None

    def add_predictor(self,predictor):
        self.predictor = predictor
        self.ocr_voter.add_predictor(self.predictor)

    def add_vocabulary_checker(self, vocab_checker):
        self.vocab_checker = vocab_checker
        self.ocr_voter.add_vocab_checker(vocab_checker)

    def compare(self, item_one, item_two, wildcard_character='¦'):
        sequences1 = [item_one]
        sequences2 = [item_two]

        sSequences1, sSequences2 = MultiSequenceAlignment.msa(sequences1, sequences2)
        """
        for i in range(len(sSequences1)):
            s1 = ''.join(['-' if element == '' else element \
                          for element in sSequences1[i]])
            s2 = ''.join(['-' if element == '' else element \
                          for element in sSequences2[i]])

            self.cpr.print(s1)
            self.cpr.print(s2)
            self.cpr.print()
        """
        s1 = ''.join([wildcard_character if element == '' else element \
                      for element in sSequences1[0]])
        s2 = ''.join([wildcard_character if element == '' else element \
                      for element in sSequences2[0]])

        return s1, s2




    def reduce_double_wildcards(self, line_1, line_2, wildcard_character='¦'):
        list_line_1 = list(line_1)
        list_line_2 = list(line_2)

        reduced_line_1 = ""
        reduced_line_2 = ""

        for character_index, character_1 in enumerate(list_line_1):
            character_2 = list_line_2[character_index]

            if character_1 == wildcard_character and character_2 == wildcard_character:
                continue

            reduced_line_1 += character_1
            reduced_line_2 += character_2


        return reduced_line_1, reduced_line_2


    def reduce_double_wildcards_specific(self, line_1, line_2, wildcard_character_1='¦', wildcard_character_2='@'):
        # mind input order here
        list_line_1 = list(line_1)
        list_line_2 = list(line_2)

        reduced_line_1 = ""
        reduced_line_2 = ""

        for character_index, character_1 in enumerate(list_line_1):
            if character_index >= len(list_line_2):
                reduced_line_1 += character_1
                continue


            character_2 = list_line_2[character_index]

            #if character_1 == wildcard_character_1 and character_2 == wildcard_character_1:
            #    continue
            if character_1 == wildcard_character_1 and character_2 == wildcard_character_2:
                continue
            #elif character_1 == wildcard_character_2 and character_2 == wildcard_character_2:
            #    continue
            elif character_1 == wildcard_character_2 and character_2 == wildcard_character_1:
                self.cpr.print("")
                continue
            #elif character_1 ==' ' and character_2 == wildcard_character_2:
            #    continue # this is really a glitch
            #elif character_2 ==' ' and character_1 == wildcard_character_2:
            #    continue # this is really a glitch


            reduced_line_1 += character_1
            reduced_line_2 += character_2


        return reduced_line_1, reduced_line_2



    def fillup_wildcarded_result(self, line_to_fill, reference_line, wildcard_character='¦'):
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



    def msa_alignment_gonzalo(self, text_1, text_2, text_3):
        # list_one = list('1. Wie funktioniert der Algorithmus')
        # list_two = list('2. Wie funktioniert hier der Algorithmus')  # this is the pivot element
        # list_three = list('3. Wie der Algorithmus')

        #text_1 = "had I expressed the agony I frequentl felt he would have been taught to long for its alleviation"
        #text_2 = "had I sed the agony I fefjuently felt he would have been to long for its alleviafcion"
        #text_3 = "had I expressed tbe agony I frequently felt he would have been taught to long for its alleviation"

        list_one = list(text_1)
        list_two = list(text_2)  # this is the pivot element
        list_three = list(text_3)

        res_one_1, res_two_1 = self.compare(list_one, list_two)


        res_two_2, res_three_2 = self.compare(list_two, list_three)

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

        self.cpr.print(len(res_one_1), res_one_1)
        self.cpr.print(len(pivot_msa), pivot_msa)
        self.cpr.print(len(res_three_2), res_three_2)
        #if res_one_1.__contains__("Sitz:") is True:
        #    self.cpr.print("asd")

        res_one_1_filled = self.fillup_wildcarded_result(res_one_1, pivot_msa)
        res_three_2_filled = self.fillup_wildcarded_result(res_three_2, pivot_msa)

        res_final_1 = res_one_1_filled
        res_final_2 = pivot_msa
        # res_final_3 = res_three_2
        res_final_3 = res_three_2_filled
        """
        res_final_1, holder1 = self.compare(list_res_one_1, list_pivot_msa)
        res_final_2 = pivot_msa
        res_final_3, holder2 = self.compare(list_res_three_2, list_pivot_msa)
        """
        #j4t
        #rres_final_1, rholder1 = self.compare(list_pivot_msa, list_res_one_1)
        #rres_final_2 = pivot_msa
        #rres_final_3, rholder2 = self.compare( list_pivot_msa, list_res_three_2)
        return res_final_1, res_final_2, res_final_3


    def msa_alignment_skbio(self, text_1, text_2, text_3):
        from skbio.alignment import global_pairwise_align, make_identity_substitution_matrix

        from multi_sequence_alignment.scikit_custom_sequence_ocr import CustomSequence


        #
        gap_open_penalty = 1
        gap_extend_penalty = 1
        #substitution_matrix_b50 =CustomSequence.blosum50 # just an example

        try:
            """    
            alignment, score, start_end_positions = local_pairwise_align_ssw(
                DNA("ACTAAGGCTCTCTACCCCTCTCAGAGA"),
                DNA("ACTAAGGCTCCTAACCCCCTTTTCTCAGA")
            )
            """
            # todo sequence/_sequence.py is missing proper encoding, this has to fix to make this work completely atm workaround: replace non ascii with '?'
            # also sequence/_grammared_sequence.py
            #cs1 = CustomSequence("Hallo das ist ein Test überkrass")
            #cs2 = CustomSequence("H4llo das ist Test überkraass")
            cs1 = CustomSequence(text_1)
            cs2 = CustomSequence(text_2)
            cs3 = CustomSequence(text_3)

            #substitution_matrix_unity = cs2.create_unity_sequence_matrix()
            substitution_matrix_equal = make_identity_substitution_matrix(1,-1,cs2.create_charset_string())

            #alignment, score, start_end_positions = local_pairwise_align(cs1, cs2, gap_open_penalty, gap_extend_penalty, substitution_matrix_unity)

            alignment12, score12, start_end_positions12 = global_pairwise_align(cs1, cs2, gap_open_penalty, gap_extend_penalty, substitution_matrix_equal)
            alignment23, score23, start_end_positions23 = global_pairwise_align(cs2, cs3, gap_open_penalty, gap_extend_penalty, substitution_matrix_equal)


            #alignment3, score3, start_end_positions3 = global_pairwise_align("Hallo das ist ein Test", "H4llo das ist Test", gap_open_penalty, gap_extend_penalty, substitution_matrix_equal)
            #res_one_1, res_two_1 = self.compare(list_one, list_two)

            #res_two_2, res_three_2 = self.compare(list_two, list_three)
            res_one_1 = str(alignment12._seqs[0])
            res_two_1 = str(alignment12._seqs[1])
            res_two_2 = str(alignment23._seqs[0])
            res_three_2 = str(alignment23._seqs[1])

            list_res_one_1 = list(res_one_1)
            list_res_two_1 = list(res_two_1)

            list_res_two_2 = list(res_two_2)
            list_res_three_2 = list(res_three_2)

            list_pivot_msa = None
            pivot_msa = None
            if len(list_res_two_1) >= len(list_res_two_2):
                # if len(list_res_two_1) > len(list_res_two_2):
                list_pivot_msa = list_res_two_1
                pivot_msa = res_two_1
            else:
                list_pivot_msa = list_res_two_2
                pivot_msa = res_two_2

            self.cpr.print(len(res_one_1), res_one_1)
            self.cpr.print(len(pivot_msa), pivot_msa)
            self.cpr.print(len(res_three_2), res_three_2)
            # if res_one_1.__contains__("Sitz:") is True:
            #    self.cpr.print("asd")

            res_one_1_filled = self.fillup_wildcarded_result(res_one_1, pivot_msa, '@')
            res_three_2_filled = self.fillup_wildcarded_result(res_three_2, pivot_msa, '@')

            res_final_1 = res_one_1_filled
            res_final_2 = pivot_msa
            # res_final_3 = res_three_2
            res_final_3 = res_three_2_filled
            return res_final_1, res_final_2, res_final_3


        except Exception as ex:
            tr = inspect.trace()
            self.cpr.printex("msa_handler.py Exception raised in %s" % tr[-1][3],ex)



    def pairwise_unicode(self, text_1, text_2, wildcard_character='¦', gap_config=None, add_leading_gapchar=False):

        if gap_config is None:
            points_identical_char = 2
            penalty_non_identical_char = -1.3 #-1
            penalty_opening_gap = -0.5 #-0.5
            penalty_extending_gap  = -0.4

        else:
            points_identical_char = gap_config.points_identical_char
            penalty_non_identical_char = gap_config.penalty_non_identical_char
            penalty_opening_gap = gap_config.penalty_opening_gap
            penalty_extending_gap = gap_config.penalty_extending_gap

        # this function fixes an issue in algorithm which crashes at certain beginnning chars
        def add_gapchar_at_start(text, wildcard_character='¦'):
            return wildcard_character + text

        if add_leading_gapchar is True:
            text_1 = add_gapchar_at_start(text_1)
            text_2 = add_gapchar_at_start(text_2)

        text_1_uclist = TypeCasts.convert_string_to_unicode_list(text_1)
        text_2_uclist = TypeCasts.convert_string_to_unicode_list(text_2)
        wildcard_character_uclist = TypeCasts.convert_string_to_unicode_list(wildcard_character)


        def custom_match_fn(charA, charB):
            similarity_1 = "l1j"
            similarity_1_uclist = TypeCasts.convert_string_to_unicode_list(similarity_1)

            match = points_identical_char
            mismatch = penalty_non_identical_char
            gap_match = points_identical_char-0.5
            gap_char = wildcard_character_uclist[0]

            if charA == charB:
                return match
            elif charA == gap_char or charB == gap_char:
                return gap_match

            elif self.config.MSA_BEST_USE_MSA_SIMILARITIES:

                for sim in MsaSimilarities.sims:
                    if charA in sim and charB in sim:
                        return gap_match-MsaSimilarities.similar_but_not_same_penalty

            return mismatch

        try:
            #ms without match fn  match_fn = identity_match_custom(points_identical_char, penality_non_identical_char, wildcard_character),
            alignment12 = pairwise2.align.globalcs(text_1_uclist, text_2_uclist,custom_match_fn, penalty_opening_gap,
                                                         penalty_extending_gap, gap_char=wildcard_character_uclist,
                                                         penalize_end_gaps=False)

            if len(alignment12) == 0:
                self.cpr.printw("msa_handler.py Alignment between, ",text_1, "and",text_2," was not possible just padding up results")
                len_text_1 = len(text_1)
                len_text_2 = len(text_2)
                if len_text_1 > len_text_2:
                    text_2_padded = Random.append_pad_values(text_2,len_text_1-len_text_2,wildcard_character)
                    return text_1, text_2_padded
                else:
                    text_1_padded = Random.append_pad_values(text_1, len_text_2-len_text_1, wildcard_character)
                    return text_1_padded, text_2

            text_1_al = TypeCasts.convert_unicodelist_to_string(alignment12[0][0])
            text_2_al = TypeCasts.convert_unicodelist_to_string(alignment12[0][1])
            return text_1_al, text_2_al
        except Exception as ex:
            tr = inspect.trace()
            self.cpr.printex("msa_handler.py Exception in pairwise alignment unicode-biopython", ex)
            self.cpr.printex("trace is", tr)

    def msa_alignment_biopython(self, text_A, text_B, text_C, wildcard_character='¦', print_output=False, recursive=True):

        try:
            #text_A = "had I expressed the agony I frequentl felt he would have been taught to long for its alleviation"
            #text_B = "had I sed the agony I fefjuently felt he would have been to long for its alleviafcion"
            #text_C = "had I expressed tbe agony I frequently felt he would have been taught to long for its alleviation"
            if "T I" in text_A:
                self.cpr.self.cpr.print("T I there")
                pass

            # stringify results to make also empty stuff comparable
            def stringify_results(text):
                if text is False or text is True or text is None or text == '' or text =="":
                    return '', True
                return text, False

            text_A, text_A_empty = stringify_results(text_A)
            text_B, text_B_empty = stringify_results(text_B)
            text_C, text_C_empty = stringify_results(text_C)

            if text_A_empty and text_B_empty:
                res_1_final = Random.append_pad_values('',len(text_C),wildcard_character)
                res_2_final = Random.append_pad_values('',len(text_C),wildcard_character)
                res_3_final = text_C
                return  res_1_final, res_2_final, res_3_final
            elif text_A_empty and text_C_empty:
                res_1_final = Random.append_pad_values('',len(text_B),wildcard_character)
                res_2_final = text_B
                res_3_final = Random.append_pad_values('',len(text_B),wildcard_character)
                return  res_1_final, res_2_final, res_3_final

            elif text_B_empty and text_C_empty:
                res_1_final = text_A
                res_2_final = Random.append_pad_values('',len(text_A),wildcard_character)
                res_3_final = Random.append_pad_values('',len(text_A),wildcard_character)
                return  res_1_final, res_2_final, res_3_final

            text_Ab, text_Ba = self.pairwise_unicode(text_A, text_B, wildcard_character,None,True)
            # text_Bc_old, text_Cb_old = self.pairwise_unicode(text_B, text_C, wildcard_character,None,True)
            text_Cb, text_Bc = self.pairwise_unicode(text_C, text_B, wildcard_character, None, True)
            self.cpr.print("text_Ab..", text_Ab)
            self.cpr.print("text_Ba..", text_Ba)
            self.cpr.print("text_Bc..", text_Bc)
            self.cpr.print("text_Cb..", text_Cb)

            # p.identical,p.non_identical,p.opening_gap,p.extending_ap
            #gap_config_big_pivot = GapConfig(4, -4, -4, -2)
            text_Babc, text_Bcba = self.pairwise_unicode(text_Ba, text_Bc, wildcard_character)

            self.cpr.print("text_Babc", text_Babc)
            self.cpr.print("text_Bcba", text_Bcba)


            text_Af, text_BabcfA = self.pairwise_unicode(text_Ab, text_Babc, wildcard_character)
            # text_Bf, text_BabcfB = self.pairwise_unicode(text_B, text_Babc, wildcard_character)
            text_Cf, text_BabcfC = self.pairwise_unicode(text_Cb, text_Babc, wildcard_character)

            self.cpr.print("text_Af..", text_Af)
            self.cpr.print("text_Babc", text_Babc)
            self.cpr.print("text_Cf..", text_Cf)

            #text_Af_r = self.reduce_double_wildcards_specific(text_Af, text_BabcfA,'@',wildcard_character)[0].replace('@',wildcard_character)
            #text_Bf_r = self.reduce_double_wildcards_specific(text_Bf, text_BabcfB,'@',wildcard_character)[0].replace('@',wildcard_character)
            #text_Cf_r = self.reduce_double_wildcards_specific(text_Cf, text_BabcfC,'@',wildcard_character)[0].replace('@',wildcard_character)

            #print("text_Af.r", text_Af_r)
            #print("text_Bf.r", text_Bf_r)
            #print("text_Cf.r", text_Cf_r)


            #if "Tätigkeit" in text_Af:
            #    print("asd")

            res_final_1 = text_Af
            res_final_2 = text_Babc
            res_final_3 = text_Cf

            if len(res_final_1) != len(res_final_2) or len(res_final_1) !=  len(res_final_3) \
                    or len(res_final_2) !=  len(res_final_3):
                self.cpr.print("no equal lengths in alignment!") #todo this adds wildcard if the case, but could be problemati
                if recursive is True: # try realign once recursively
                    res_final_1, res_final_2, res_final_3 = self.msa_alignment_biopython(res_final_1, res_final_2, res_final_3,
                                                                   wildcard_character, print_output, recursive=False)


                final_arrs = [res_final_1, res_final_2, res_final_3]
                maxlen = max([len(res_final_1), len(res_final_2), len(res_final_3)])
                # maxindex = np.argmax([len(res_final_1), len(res_final_2), len(res_final_3)])  # this takes in priorisation in case the chars are same
                for current_res_index, current_res in enumerate(final_arrs):
                    current_len = len(current_res)
                    pad_size_needed = maxlen-current_len
                    if pad_size_needed >=1:
                        new_res = Random.append_pad_values(current_res,pad_size_needed,wildcard_character)
                        final_arrs[current_res_index] = new_res

                res_final_1 = final_arrs[0]
                res_final_2 = final_arrs[1]
                res_final_3 = final_arrs[2]


            return res_final_1, res_final_2, res_final_3
        except Exception as ex:
            tr = inspect.trace()

            self.cpr.printex("msa_handler.py Exception within alignment algo ", ex)
            self.cpr.printex("trace", tr)

    def msa_alignment_biopython_old(self, text_1, text_2, text_3, wildcard_character='¦'):

        wildcard_character2 = '@'

        #text_1 = "Das erster text"
        #text_2 = "Das zweiter text"
        #text_3 = "Das dritter text"
        #works
        #text_1 = "Geschäftsjahr:Kalenderjahr."
        #text_2 = "Geschäftsjahr: Kalenderjahr."
        #text_3 = "Geschtaftsjahr:Kalenderjahr."


        #that's the isolated problem case


        """
        align1 = MultipleSeqAlignment([
            SeqRecord(Seq("ACTGCTAGCTAG", generic_dna), id="Alpha"),
            SeqRecord(Seq("ACT-CTAGCTAG", generic_dna), id="Beta"),
            SeqRecord(Seq("ACTGCTAGDTAG", generic_dna), id="Gamma"),
        ])

        align2 = MultipleSeqAlignment([
            SeqRecord(Seq("GTCAGC-AG", generic_dna), id="Delta"),
            SeqRecord(Seq("GACAGCTAG", generic_dna), id="Epsilon"),
            SeqRecord(Seq("GTCAGCTAG", generic_dna), id="Zeta"),
        ])

        align3 = MultipleSeqAlignment([
            SeqRecord(Seq("ACTAGTACAGCTG", generic_dna), id="Eta"),
            SeqRecord(Seq("ACTAGTACAGCT-", generic_dna), id="Theta"),
            SeqRecord(Seq("-CTACTACAGGTG", generic_dna), id="Iota"),
        ])
              
        my_alignments = [align1, align2, align3]
        """
        """
        penalize_extend_when_opening: boolean (default: False). Whether to count an extension penalty when opening a gap. If false, a gap of 1 is only penalized an "open" penalty, otherwise it is penalized "open+extend".
        penalize_end_gaps: boolean. Whether to count the gaps at the ends of an alignment. By default, they are counted for global alignments but not for local ones. Setting penalize_end_gaps to (boolean, boolean) allows you to specify for the two sequences separately whether gaps at the end of the alignment should be counted.
        gap_char: string (default: '-'). Which character to use as a gap character in the alignment returned. If your input sequences are lists, you must change this to ['-'].
        force_generic: boolean (default: False). Always use the generic, non-cached, dynamic programming function (slow!). For debugging.
        score_only: boolean (default: False). Only get the best score, don't recover any alignments. The return value of the function is the score. Faster and uses less memory.
        one_alignment_only: boolean (default: False). Only recover one alignment.
        """
        #wildcard_character = '@'
        # http://biopython.org/DIST/docs/api/Bio.pairwise2-module.html

        #matrix = matlist.blosum62


        points_identical_char = 2
        penality_non_identical_char = -1
        penalty_opening_gap = -0.5
        penalty_extending_gap  = -0.1

        take_first_or_last = True  # True take first alignment, False take last alignment

        try:


            self.cpr.print("Biopython alignment 1", text_1, text_2)
            self.cpr.print("Biopython alignment 2", text_2, text_3)
            #if '>' in text_3:

            #text_3 = text_2

            #text_1_cp = text_1[:]
            #text_2_cp = text_2[:]
            #text_3_cp = text_3[:]

            text_1_uclist = TypeCasts.convert_string_to_unicode_list(text_1)
            text_2_uclist = TypeCasts.convert_string_to_unicode_list(text_2)
            text_3_uclist = TypeCasts.convert_string_to_unicode_list(text_3)

            wildcard_character_uclist = TypeCasts.convert_string_to_unicode_list(wildcard_character)

            alignment12_multi = pairwise2.align.globalms(text_1_uclist, text_2_uclist, points_identical_char, penality_non_identical_char,penalty_opening_gap,penalty_extending_gap, gap_char=wildcard_character_uclist,penalize_end_gaps=False)
            alignment23_multi = pairwise2.align.globalms(text_2_uclist, text_3_uclist, points_identical_char, penality_non_identical_char,penalty_opening_gap,penalty_extending_gap, gap_char=wildcard_character_uclist,penalize_end_gaps=False)

            self.cpr.print("12 one", TypeCasts.convert_unicodelist_to_string(alignment12_multi[0][0]))
            self.cpr.print("12 two", TypeCasts.convert_unicodelist_to_string(alignment12_multi[0][1]))
            self.cpr.print("23 one", TypeCasts.convert_unicodelist_to_string(alignment23_multi[0][0]))
            self.cpr.print("23 two", TypeCasts.convert_unicodelist_to_string(alignment23_multi[0][1]))

            wildcard_character_uclist2 = TypeCasts.convert_string_to_unicode_list(wildcard_character2)
            ff_compare_list = None
            if len(alignment12_multi[0][1]) > len(alignment23_multi[0][0]):
                alignmentff_multi = pairwise2.align.globalms(alignment23_multi[0][1], alignment12_multi[0][1],
                                                             points_identical_char, penality_non_identical_char,
                                                             penalty_opening_gap, penalty_extending_gap,
                                                             gap_char=wildcard_character_uclist2,
                                                             penalize_end_gaps=False)
                self.cpr.print("ff one", TypeCasts.convert_unicodelist_to_string(alignmentff_multi[0][0]))
                self.cpr.print("ff two", TypeCasts.convert_unicodelist_to_string(alignmentff_multi[0][1]))
                # alignmentee_multi = pairwise2.align.globalms(alignment23_multi[0][1], alignmentff_multi[0][1], points_identical_char, penality_non_identical_char,penalty_opening_gap,penalty_extending_gap, gap_char=wildcard_character_uclist2,penalize_end_gaps=False)
                # self.cpr.print("ee one", TypeCasts.convert_unicodelist_to_string(alignmentee_multi[0][0]))
                # self.cpr.print("ee two", TypeCasts.convert_unicodelist_to_string(alignmentee_multi[0][1]))
                if len(alignmentff_multi[0][1]) > len(alignment12_multi[0][0]):
                    redwc1, redwc2 = self.reduce_double_wildcards_specific( \
                         TypeCasts.convert_unicodelist_to_string(alignmentff_multi[0][0]), \
                        TypeCasts.convert_unicodelist_to_string(alignmentff_multi[0][1]))
                    self.cpr.print("ff onr", redwc1)
                    self.cpr.print("ff twr", redwc2)
                else:
                    redwc2 = TypeCasts.convert_unicodelist_to_string(alignmentff_multi[0][1])

                res_final_1 = TypeCasts.convert_unicodelist_to_string(alignment12_multi[0][0])
                res_final_2 = TypeCasts.convert_unicodelist_to_string(alignment12_multi[0][1])
                res_final_3 = redwc2.replace(wildcard_character2,wildcard_character) #replace the helper wildcards



                self.cpr.print("path 1")
                self.cpr.print("res_fi1", res_final_1)
                self.cpr.print("res_fi2", res_final_2)
                self.cpr.print("res_fi3", res_final_3)

                if "Eigenkapital" in res_final_1:
                    self.cpr.print("teheres a bug")

            else:
                alignmentff_multi = pairwise2.align.globalms(alignment12_multi[0][0], alignment23_multi[0][0],
                                                             points_identical_char, penality_non_identical_char,
                                                             penalty_opening_gap, penalty_extending_gap,
                                                             gap_char=wildcard_character_uclist2,
                                                             penalize_end_gaps=False)



                self.cpr.print("ff one", TypeCasts.convert_unicodelist_to_string(alignmentff_multi[0][0]))
                self.cpr.print("ff two", TypeCasts.convert_unicodelist_to_string(alignmentff_multi[0][1]))
                # alignmentee_multi = pairwise2.align.globalms(alignment23_multi[0][1], alignmentff_multi[0][1], points_identical_char, penality_non_identical_char,penalty_opening_gap,penalty_extending_gap, gap_char=wildcard_character_uclist2,penalize_end_gaps=False)
                # self.cpr.print("ee one", TypeCasts.convert_unicodelist_to_string(alignmentee_multi[0][0]))
                # self.cpr.print("ee two", TypeCasts.convert_unicodelist_to_string(alignmentee_multi[0][1]))
                if len(alignmentff_multi[0][1]) > len(alignment23_multi[0][0]):

                    alignmentffNeu_multi = pairwise2.align.globalms(alignment23_multi[0][1],
                                                                    alignmentff_multi[0][1],
                                                                  points_identical_char, penality_non_identical_char,
                                                                  penalty_opening_gap, penalty_extending_gap,
                                                                  gap_char=wildcard_character_uclist2)

                    self.cpr.print("ff onn", TypeCasts.convert_unicodelist_to_string(alignmentffNeu_multi[0][0]))
                    self.cpr.print("ff twn", TypeCasts.convert_unicodelist_to_string(alignmentffNeu_multi[0][1]))

                    # ignore
                    redwc1, redwc2 = self.reduce_double_wildcards_specific(
                        TypeCasts.convert_unicodelist_to_string(alignmentff_multi[0][0]),
                        TypeCasts.convert_unicodelist_to_string(alignmentff_multi[0][1]), wildcard_character, wildcard_character2)
                    self.cpr.print("ff onr", redwc1)
                    self.cpr.print("ff twr", redwc2)

                    if len(redwc2) > len(alignment23_multi[0][1]):
                        redwc2rep = redwc2.replace(wildcard_character2, wildcard_character)

                        alignmentff2_multi = pairwise2.align.globalms(alignment23_multi[0][1], TypeCasts.convert_string_to_unicode_list(redwc2rep),
                                                                     points_identical_char, penality_non_identical_char,
                                                                     penalty_opening_gap, penalty_extending_gap,
                                                                     gap_char=wildcard_character_uclist2)

                        self.cpr.print("ff thr", TypeCasts.convert_unicodelist_to_string(alignmentff2_multi[0][0]))
                        self.cpr.print("ff th2", TypeCasts.convert_unicodelist_to_string(alignmentff2_multi[0][1]))
                        redwc3, redwc4 = self.reduce_double_wildcards_specific(
                            TypeCasts.convert_unicodelist_to_string(alignmentff2_multi[0][0]),
                            redwc2rep, wildcard_character,
                            wildcard_character2)
                        self.cpr.print("ff th3", redwc3.replace(wildcard_character2, wildcard_character))

                        self.cpr.print("")

                else:
                    redwc1 = TypeCasts.convert_unicodelist_to_string(alignmentff_multi[0][1])

                res_final_1 = redwc1.replace(wildcard_character2, wildcard_character)
                res_final_2 = TypeCasts.convert_unicodelist_to_string(alignment23_multi[0][0])
                res_final_3 = TypeCasts.convert_unicodelist_to_string(alignment23_multi[0][1])
                self.cpr.print("path 2")
                self.cpr.print("res_fi1", res_final_1)
                self.cpr.print("res_fi2", res_final_2)
                self.cpr.print("res_fi3", res_final_3)

            if len(res_final_1) != len(res_final_2) or len(res_final_2) != len(res_final_3):
                self.cpr.print("shouldn't happen")



            return res_final_1, res_final_2, res_final_3

            if take_first_or_last is True:
                alignment12_index = 0
                alignment23_index = 0
            else:
                alignment12_index = len(alignment12_multi)-1
                alignment23_index = len(alignment23_multi)-1

            alignment12 = alignment12_multi[alignment12_index]
            alignment23 = alignment23_multi[alignment23_index]




            # experiments
            #alignmentsPW2 = pairwise2.align.globalmx("ACCGT", "ACG",points_identical_char,penality_non_identical_char, gap_char='¦')
            #alignmentsPW3 = pairwise2.align.globalxx("Übersetzerin", "Übersetzung")
            #alignmentsPW2M = pairwise2.align.globalxx("Übersetzerin", "Übersetzung",matrix)

            res_one_1 = alignment12[0][:]
            res_two_1 = alignment12[1][:]
            res_two_2 = alignment23[0][:]
            res_three_2 = alignment23[1][:]

            list_res_one_1 = res_one_1
            list_res_two_1 = res_two_1

            list_res_two_2 = res_two_2
            list_res_three_2 = res_three_2

            list_pivot_msa = None
            pivot_msa = None

            pivot_index = -1
            if len(res_two_1) >= len(res_two_2):
                # if len(list_res_two_1) > len(list_res_two_2):
                list_pivot_msa = list_res_two_1
                pivot_msa = res_two_1
                pivot_index = 0
            else:
                list_pivot_msa = list_res_two_2
                pivot_msa = res_two_2
                pivot_index = 1



            self.cpr.print(len(res_one_1), TypeCasts.convert_unicodelist_to_string(res_one_1))
            self.cpr.print(len(pivot_msa), TypeCasts.convert_unicodelist_to_string(pivot_msa))
            self.cpr.print(len(res_three_2), TypeCasts.convert_unicodelist_to_string(res_three_2))
            self.cpr.print("pivot index",pivot_index)
            # if res_one_1.__contains__("Sitz:") is True:
            #    self.cpr.print("asd")

            #return "Fake","Fake","Fake"

            USE_OLD_FILLING = False
            if USE_OLD_FILLING is True:
                res_one_1_filled = self.fillup_wildcarded_result(res_one_1, pivot_msa)
                res_three_2_filled = self.fillup_wildcarded_result(res_three_2, pivot_msa)
            else:
                # if'Stra' in res_three_2:
                #    self.cpr.print("asd")

                pivot_index = 0
                if pivot_index == 0:

                    res_one_1_cp = res_one_1[:]
                    res_three_2_cp = res_three_2[:]
                    pivot_msa_cp = pivot_msa[:]
                    res_three_2_multi = pairwise2.align.globalxx(res_three_2_cp, pivot_msa_cp, gap_char= wildcard_character_uclist, force_generic=False)


                    new_pivot = res_three_2_multi[0][0]
                    res_three_2_filled = res_three_2_multi[0][1]
                    self.cpr.print("new_pivot_......", TypeCasts.convert_unicodelist_to_string(new_pivot))
                    self.cpr.print("res_thr_2_filled",TypeCasts.convert_unicodelist_to_string(res_three_2_filled))

                    res_one_1_multi_2 = pairwise2.align.globalxx(res_one_1_cp, pivot_msa, gap_char= wildcard_character_uclist, force_generic=False)
                    res_one_1_filled = res_one_1_multi_2[0][0]
                    self.cpr.print("res_one_1_filled",TypeCasts.convert_unicodelist_to_string(res_one_1_filled))


                    self.cpr.print("a")

                elif pivot_index == 1:

                    #res_one_1_multi = pairwise2.align.globalms(res_one_1, pivot_msa, points_identical_char,
                    #                                             penality_non_identical_char, penalty_opening_gap,
                    #                                             penalty_extending_gap, gap_char='¦',
                    #                                             penalize_end_gaps=False)

                    res_one_1_cp = res_one_1[:]
                    pivot_msa_cp = pivot_msa[:]
                    res_one_1_multi = pairwise2.align.globalxx(res_one_1_cp,pivot_msa_cp, gap_char=wildcard_character_uclist, force_generic=False)
                    res_one_1_filled = res_one_1_multi[0][0]
                    res_three_2_filled = res_three_2




            #res_one_1_filledOld = self.fillup_wildcarded_result(res_one_1, pivot_msa, '¦')
            #res_three_2_filledOld = self.fillup_wildcarded_result(res_three_2, pivot_msa, '¦')

            res_final_1 = TypeCasts.convert_unicodelist_to_string(res_one_1_filled)
            res_final_2 = TypeCasts.convert_unicodelist_to_string(new_pivot)
            # res_final_3 = res_three_2
            res_final_3 = TypeCasts.convert_unicodelist_to_string(res_three_2_filled)
            self.cpr.print("j4t-new")
            self.cpr.print(res_final_1)
            self.cpr.print(res_final_2)
            self.cpr.print(res_final_3)
            #self.cpr.print("j4t-old")
            #self.cpr.print(res_one_1_filledOld)
            #self.cpr.print(res_final_2)
            #self.cpr.print(res_three_2_filledOld)
            return res_final_1, res_final_2, res_final_3

        except Exception as ex:
            self.cpr.printex("msa_handler.py exception", ex)

        #self.cpr.print(pairwise2.format_alignment(*alignmentsPW[0]))
        #self.cpr.print(pairwise2.format_alignment(*alignmentsPW[1]))



        # alignment3, score3, start_end_positions3 = global_pairwise_align("Hallo das ist ein Test", "H4llo das ist Test", gap_open_penalty, gap_extend_penalty, substitution_matrix_equal)
        # res_one_1, res_two_1 = self.compare(list_one, list_two)

        # res_two_2, res_three_2 = self.compare(list_two, list_three)


    def align_three_texts(self, text_1, text_2, text_3, wildcard_character = '¦', print_output=False):
        MODE_GONZALO = 'gonzalo'
        MODE_SKBIO = 'scikit-bio_alignment'
        MODE_BIOPYTHON = 'biopython'
        MODE = MODE_BIOPYTHON

        if MODE == MODE_GONZALO:
            res_final_1, res_final_2, res_final_3 = self.msa_alignment_gonzalo(text_1, text_2, text_3)

        elif MODE == MODE_SKBIO:
            res_final_1, res_final_2, res_final_3 = self.msa_alignment_skbio(text_1, text_2, text_3)
        elif MODE == MODE_BIOPYTHON:
            res_final_1, res_final_2, res_final_3 = self.msa_alignment_biopython(text_1, text_2, text_3, wildcard_character, print_output)

        return res_final_1, res_final_2, res_final_3


    def get_best_of_three_wordwise(self, line_1, line_2, line_3, use_charconfs, use_searchspaces):
        wildcard_character = '¦'
        PRINT_RESULTS = True
        PRINT_ALIGNMENT_PROCESS = False

        # iterate words
        def get_max_wordlen(line_to_check):
            if line_to_check is None or line_to_check is False or line_to_check is True:
                return -1

            word_indices = line_to_check.word['text'].keys()
            if len(word_indices) == 0:
                highest_word = 0
            else:
                highest_word = max(word_indices)
            return highest_word

        def get_word_from_line(line_to_check, word_index, return_val_empty=""):
            if line_to_check is None or line_to_check is False or line_to_check is True:
                return return_val_empty

            word_obtained = line_to_check.word["text"].get(word_index, return_val_empty)
            return word_obtained

        def update_word(line_in, word_index, new_value, remove_wildcards=False):

            if remove_wildcards is True:
                new_value = new_value.replace(wildcard_character, '')  # remove wildcards

            line_in.update_textspace(new_value, wildcard_character, widx=word_index)


        def sort_words_longest_mid(word1, word2, word3):
            words = [word1, word2, word3]

            wlongest_index = np.argmax([len(word1), len(word2), len(word3)])

            if wlongest_index == 1:
                words_sorted = words
            else:
                longest_word = words[wlongest_index]
                words_sorted = words[:]
                words_sorted.pop(wlongest_index)
                words_sorted.insert(1, longest_word)

            return words_sorted, wlongest_index


        def reverse_mid_sort(al_word1,alword2, alword3, wlongest_index):
            words_aligned = [al_word1, alword3]
            words_aligned.insert(wlongest_index, alword2)
            return words_aligned

        m1 = get_max_wordlen(line_1)
        m2 = get_max_wordlen(line_2)
        m3 = get_max_wordlen(line_3)
        max_range_word = int(max(m1, m2, m3)+1)  # add a one because it starts with zero

        try:
            for current_word_index in range(0, max_range_word):
                word1 = get_word_from_line(line_1, current_word_index)
                word2 = get_word_from_line(line_2, current_word_index)
                word3 = get_word_from_line(line_3, current_word_index)
                self.cpr.print("word   1:", word1)
                self.cpr.print("word   2:", word2)
                self.cpr.print("word   3:", word3)



                # sort by length (longest has index 1)
                words_sorted, wlongest_index = sort_words_longest_mid(word1, word2, word3)
                # if wildcard_character is True or wildcard_character is False:
                #    print("asd")

                word1_al, word2_al, word3_al = self.align_three_texts(words_sorted[0], words_sorted[1], \
                                                                            words_sorted[2], wildcard_character, PRINT_ALIGNMENT_PROCESS)

                # sort back ...
                words_aligned = reverse_mid_sort(word1_al, word2_al, word3_al, wlongest_index)
                if len(words_aligned[0]) != len(words_aligned[1]) or len(words_aligned[1]) != len(words_aligned[2]):
                    self.cpr.print("shouldn't be")
                else:
                    deletion_marker = "¡"
                    deletion_needed = False
                    word_len_aligned = len(words_aligned[0])
                    for i in range(0, word_len_aligned):
                        only_wildcards_at_index = True
                        for word_current in words_aligned:
                            current_letter = list(word_current)[i]
                            if current_letter != wildcard_character:
                                only_wildcards_at_index = False

                        if only_wildcards_at_index:
                            for word_index, word_current in enumerate(words_aligned):
                                deletion_needed = True
                                word_c_list = list(word_current)
                                word_c_list[i] = deletion_marker
                                words_aligned[word_index] = "".join(word_c_list)

                    if deletion_needed is True:
                        for word_index, word_current in enumerate(words_aligned):
                            words_aligned[word_index] = words_aligned[word_index].replace(deletion_marker,"")

                if self.config.MSA_BEST_WORDWISE_DROP_LAST_WORD_SC:
                    # filter out last word only special char
                    if current_word_index == max_range_word-1:
                        if len(words_aligned[0]) == 1:
                            wc_count = 0  # number of wildcards
                            sc_count = 0  # number of special characters
                            for word in words_aligned:
                                if word == wildcard_character:
                                    wc_count += 1
                                elif Random.is_special_character(word):
                                    sc_count += 1

                            if wc_count == 2 and sc_count == 1:
                                print("won't update last word because seems wrong")
                                break  # just don't update the last word

                self.cpr.print("word_al 1:", words_aligned[0])
                self.cpr.print("word_al 2:", words_aligned[1])
                self.cpr.print("word_al 3:", words_aligned[2])


                # if "-" in word1 or "-" in word2 or "-" in word3:
                #    print("a wild dash appears")
                #    dash_there = True


                update_word(line_1, current_word_index, words_aligned[0])
                update_word(line_2, current_word_index, words_aligned[1])
                update_word(line_3, current_word_index, words_aligned[2])


            if use_charconfs:
                if use_searchspaces is False:
                    best, best_stripped = self.ocr_voter.vote_best_of_three_charconfs(line_1, line_2, line_3, 1,
                                                                                wildcard_character)  # res two is the best element
                else:
                    best, best_stripped = self.ocr_voter.vote_best_of_three_charconfs_searchspaces(line_1, line_2, line_3, 1,
                                                                                wildcard_character)

                best_stripped_non_multi_whitespace = ' '.join(best_stripped.split())

            if PRINT_RESULTS:


                self.cpr.print("best         ", best)
                self.cpr.print("best_stripped", best_stripped)
                self.cpr.print("best______nmw", best_stripped_non_multi_whitespace)

                #if dash_there == True:
                #    print("dashresult")
                #if "DM 10" in best_stripped:
                #    print("beep")

            return best_stripped_non_multi_whitespace
        except Exception as ex:
            tr = inspect.trace()
            self.cpr.printex("msa_handler.py exception", ex)
            self.cpr.printex("tr", tr)


    def get_best_of_three(self, text_1, text_2, text_3, use_charconfs = False, line_1 = None, line_2 = None, line_3 = None, use_searchspaces=False):
        PRINT_RESULTS = True
        wildcard_character = '¦'

        res_final_1, res_final_2, res_final_3 = self.align_three_texts(text_1, text_2, text_3, wildcard_character)
        #if "Aufsichtsrat:" in res_final_1:
        self.cpr.print("my final resolutions before vote")
        self.cpr.print("res_final_1", res_final_1)
        self.cpr.print("res_final_2", res_final_2)
        self.cpr.print("res_final_3", res_final_3)

        if use_charconfs is True:

            # update the line info with resolutions
            line_1.update_textspace(res_final_1, wildcard_character)
            line_2.update_textspace(res_final_2, wildcard_character)
            line_3.update_textspace(res_final_3, wildcard_character)

            if use_searchspaces is False:
                best, best_stripped = self.ocr_voter.vote_best_of_three_charconfs(line_1, line_2, line_3, 1,
                                                                                  wildcard_character)  # res two is the best element
            else:
                best, best_stripped = self.ocr_voter.vote_best_of_three_charconfs_searchspaces(line_1, line_2, line_3,
                                                                                               1,
                                                                                               wildcard_character)

            # This is the voting algorithm -
            #best, best_stripped = self.ocr_voter.vote_best_of_three_charconfs(line_1, line_2, line_3, 1, wildcard_character)  # res two is the best element
            best_stripped_non_multi_whitespace = ' '.join(best_stripped.split())

        else:
            # todo add searchspaces possibility here
            # This is the voting algorithm -
            best, best_stripped = self.ocr_voter.vote_best_of_three_simple(res_final_1, res_final_2, res_final_3, 1,wildcard_character)  # res two is the best element
            best_stripped_non_multi_whitespace = ' '.join(best_stripped.split())

        if PRINT_RESULTS:
            self.cpr.print("A:", res_final_1)
            self.cpr.print("B:", res_final_2)
            self.cpr.print("C:", res_final_3)
            self.cpr.print("D:", best)
            self.cpr.print("E:", best_stripped)
            self.cpr.print("F:", best_stripped_non_multi_whitespace)
        return best_stripped_non_multi_whitespace