from multi_sequence_alignment.msa_algorithm import MultiSequenceAlignment
import inspect
from Bio import pairwise2
from n_dist_keying.ocr_voter import OCRVoter
from utils.random import Random
import numpy as np
from utils.typecasts import TypeCasts
from utils.conditional_print import ConditionalPrint
from configuration.configuration_handler import ConfigurationHandler
from n_dist_keying.table_handler import TableHandler

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

        if self.config.TABLE_RECOGNITION_ENABLED:
            self.table_handler = TableHandler()

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

    def get_word_from_line(self, line_to_check, word_index, return_val_empty=""):
        if line_to_check is None or line_to_check is False or line_to_check is True:
            return return_val_empty

        word_obtained = line_to_check.word["text"].get(word_index, return_val_empty)
        return word_obtained


    def get_best_of_three_wordwise(self, line_1, line_2, line_3, use_charconfs, use_searchspaces):

        wildcard_character = '¦'
        PRINT_RESULTS = True
        PRINT_ALIGNMENT_PROCESS = False

        lines = [line_1, line_2, line_3]

        is_table = []

        table_line_preselected = False
        best = None
        best_stripped = None
        if self.config.TABLE_RECOGNITION_ENABLED:
            is_table_line_0 = self.table_handler.recognize_a_line(lines[0])
            is_table_line_1 = self.table_handler.recognize_a_line(lines[1])
            is_table_line_2 = self.table_handler.recognize_a_line(lines[2])
            is_table.extend([is_table_line_0, is_table_line_1, is_table_line_2])
            one_is_table = is_table_line_0 or is_table_line_1 or is_table_line_2
            if one_is_table:

                # define best and best_stripped
                for line_index, line in enumerate(lines):
                    # just take abbyy table line # 'Ocro' # 'Tess'
                    if "Tess" in line.name[0]:
                        best = line.textstr
                        best_stripped = best.replace(wildcard_character,"")
                        table_line_preselected = True
                        break
                # if there was a valid table line preselected skip all processing and take the selected line
                if table_line_preselected:
                    predef_seg_counter = [] # just a filler array for seg counter
                    best_stripped_non_multi_whitespace = ' '.join(best_stripped.split())
                    best_stripped_non_multi_whitespace, text_seg = self.do_last_steps(best, best_stripped,
                                                                                      best_stripped_non_multi_whitespace,
                                                                                      predef_seg_counter,
                                                                                      PRINT_RESULTS)
                    #with open("checkfile_tables.txt", "a") as myfile:
                    #    myfile.write(
                    #       best_stripped_non_multi_whitespace+"\n")

                    #return best_stripped_non_multi_whitespace, text_seg

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
            seg_counter = []
            for current_word_index in range(0, max_range_word):
                word1 = self.get_word_from_line(line_1, current_word_index)
                word2 = self.get_word_from_line(line_2, current_word_index)
                word3 = self.get_word_from_line(line_3, current_word_index)
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
                            scs_list = []
                            for word in words_aligned:
                                if word == wildcard_character:
                                    wc_count += 1
                                elif Random.is_special_character(word):
                                    sc_count += 1
                                    scs_list.append(word)

                            if wc_count == 2 and sc_count == 1:
                                if not "%" in scs_list: # ignore percentages because this case is often in tables
                                    # print("won't update last word because seems wrong")
                                    break  # just don't update the last word



                self.cpr.print("word_al 1:", words_aligned[0])
                self.cpr.print("word_al 2:", words_aligned[1])
                self.cpr.print("word_al 3:", words_aligned[2])

                update_word(line_1, current_word_index, words_aligned[0])
                update_word(line_2, current_word_index, words_aligned[1])
                update_word(line_3, current_word_index, words_aligned[2])
                #if "COLONIA" in words_aligned[0]:
                #    stop="STOP"
                #Creates the segment counter for wordbbox
                seg_counter.extend([current_word_index]*(max([len(words_aligned[0]),len(words_aligned[1]),len(words_aligned[2])])))
                if current_word_index < max_range_word-1 and max([len(words_aligned[0]),len(words_aligned[1]),len(words_aligned[2])]) > 0:
                    seg_counter.append(-1)

            if self.config.MSA_BEST_WORDWISE_CRUNCH_WORDS:
                # crunch neighboring words which are similar, this changes the wor assignment in the line objects by reference
                # if similarity was detected
                self.crunch_neighbouring_words( max_range_word, wildcard_character, line_1, line_2, line_3)


            if use_charconfs:
                if use_searchspaces is False:
                    best, best_stripped = self.ocr_voter.vote_best_of_three_charconfs(line_1, line_2, line_3, 1,
                                                                                wildcard_character)  # res two is the best element
                else:
                    best, best_stripped = self.ocr_voter.vote_best_of_three_charconfs_searchspaces(line_1, line_2, line_3, 1,
                                                                                wildcard_character)

                best_stripped_non_multi_whitespace = ' '.join(best_stripped.split())
                best_stripped_non_multi_whitespace, text_seg = self.do_last_steps(best, best_stripped,
                                                                             best_stripped_non_multi_whitespace,
                                                                             seg_counter,
                                                                             PRINT_RESULTS)

                return best_stripped_non_multi_whitespace, text_seg

            else:
                print("not implemented yet")
                # todo implement case without charconfs


        except Exception as ex:
            tr = inspect.trace()
            self.cpr.printex("msa_handler.py exception", ex)
            self.cpr.printex("tr", tr)


    def do_last_steps(self, best, best_stripped, best_stripped_non_multi_whitespace, seg_counter, PRINT_RESULTS):
        text_seg = {}

        if PRINT_RESULTS:

            self.cpr.print("best         ", best)
            self.cpr.print("best_stripped", best_stripped)
            self.cpr.print("best______nmw", best_stripped_non_multi_whitespace)

        if len(best) == len(seg_counter) and len(best.replace("¦", "").strip()) != 0:
            # seg_counter = np.array(seg_counter)
            # Delete all wc
            wc_pos = [number for number, symbol in enumerate(best) if symbol == "¦"]
            for pos in reversed(wc_pos): del seg_counter[pos]
            # Delete the ws if the first or the second word was deleted
            if seg_counter[0] == -1: del seg_counter[0]
            if seg_counter[-1] == -1: del seg_counter[-1]
            # Delete the ws if a word in the middle was delete
            if best_stripped[0] == " ": best_stripped = best_stripped[1:]
            wc_pos = [number for number, symbol in enumerate(best_stripped.replace("  ", "¦")) if symbol == "¦"]
            for pos in reversed(wc_pos):
                del seg_counter[pos]
            # seg_counter = [number for number in seg_counter if number != -1]

            if len(best_stripped_non_multi_whitespace) == len(seg_counter):
                ws_pos = np.where(np.array(seg_counter) == -1)
                ws_pos = np.ndarray.tolist(ws_pos[0])
                ws_pos.append(len(seg_counter))
                last_pos = 0
                for ws in ws_pos:
                    text_seg[float(seg_counter[ws - 1])] = best_stripped_non_multi_whitespace[last_pos:ws]
                    last_pos = ws + 1
            else:
                text_seg[-1.0] = best_stripped_non_multi_whitespace
        else:
            text_seg[-1.0] = best_stripped_non_multi_whitespace

        return best_stripped_non_multi_whitespace, text_seg



    def crunch_neighbouring_words(self,max_range_word, wildcard_character, line_1, line_2, line_3):
        lines = [line_1, line_2, line_3]

        def get_other_index_wcs(longest_wcs_counter, oc_index):
            for wcs_index, wcs_item in enumerate(longest_wcs_counter):
                if oc_index != wcs_index:
                    return wcs_index

        # extract features from each word with current_word_index
        words_and_feats = []
        for current_word_index in range(0, max_range_word):
            word1 = self.get_word_from_line(line_1, current_word_index)
            word2 = self.get_word_from_line(line_2, current_word_index)
            word3 = self.get_word_from_line(line_3, current_word_index)
            feats_word = self.get_word_column_feats(word1, word2, word3, wildcard_character)
            words_and_feats.append(([word1, word2, word3], feats_word))

        # if there less than two following words, there is nothing to crunch
        if len(words_and_feats) <= 1:
            return

        for waf_index in range(0, len(words_and_feats) - 1):
            # words = words_and_feats[waf_index][0]

            feats = words_and_feats[waf_index][1][0]
            oc_index = words_and_feats[waf_index][1][1]
            longest_wcs_counter = words_and_feats[waf_index][1][2]  # longest wildcard streaks
            # words_next = words_and_feats[waf_index + 1][0]
            feats_next = words_and_feats[waf_index + 1][1][0]
            oc_index_next = words_and_feats[waf_index + 1][1][1]
            longest_wcs_counter_next = words_and_feats[waf_index + 1][1][2]  # longest wildcard streaks
            # if "Juli" in words:
            #    print("asd")

            if self.WordColumnFeats.FEATURE_WAS_PROCESSED in feats \
                    or self.WordColumnFeats.FEATURE_WAS_PROCESSED in feats_next:
                #print("skip_a_feat_cr")
                continue

            if self.WordColumnFeats.HIGH_WILDCARD_RATIO_IN_MOST_ITEMS in feats \
                    and self.WordColumnFeats.HIGH_WILDCARD_RATIO_IN_ONE_ITEM in feats_next \
                    and oc_index == oc_index_next:

                wc_substraction_count = longest_wcs_counter_next[oc_index_next][0]
                for line_index, line in enumerate(lines):
                    if line_index != oc_index:
                        # delete wildcards
                        word_to_change = line.word["text"][waf_index]
                        word_start = line.data["word_match"].index(waf_index)
                        start = word_start + len(word_to_change) - wc_substraction_count
                        end = start + len(word_to_change) - wc_substraction_count
                        line.delete_stuff_at(start, end)
                        # print("cp")

                    else:

                        # shift content from current word to next
                        word_to_shift = line.word["text"][waf_index]
                        shifted_content = word_to_shift[len(word_to_shift) - wc_substraction_count:]

                        indexs = line.word["UID"][waf_index + 1]
                        end = line.data["word_match"].index(waf_index + 1)
                        start = end - len(shifted_content)
                        line.update_stuff_at(start, end, waf_index + 1, indexs)

                        # delete wildcards in next word
                        word_to_change = line.word["text"][waf_index + 1]
                        word_start = line.data["word_match"].index(waf_index + 1)

                        start = word_start + len(shifted_content)
                        line.delete_stuff_at(start, start + wc_substraction_count)
                        # print("cp")

                # mark the current and next feature space as processed
                words_and_feats[waf_index][1][0].append(self.WordColumnFeats.FEATURE_WAS_PROCESSED)
                words_and_feats[waf_index + 1][1][0].append(self.WordColumnFeats.FEATURE_WAS_PROCESSED)
                # update current features variables for next condition
                feats = words_and_feats[waf_index][1][0]
                feats_next = words_and_feats[waf_index + 1][1][0]

                # print(words)
                # print(words_next)
                # print("t")

            if self.WordColumnFeats.HIGH_WILDCARD_RATIO_IN_ONE_ITEM in feats \
                    and self.WordColumnFeats.HIGH_WILDCARD_RATIO_IN_MOST_ITEMS in feats_next \
                    and oc_index == oc_index_next:

                # get the index which shall get substracted
                index_subst = get_other_index_wcs(longest_wcs_counter, oc_index)
                wc_substraction_count = longest_wcs_counter_next[index_subst][0]

                for line_index, line in enumerate(lines):
                    if line_index != oc_index:
                        start = line.data["word_match"].index(waf_index + 1)
                        line.delete_stuff_at(start, start + wc_substraction_count)
                    else:
                        # word_base = line.word["text"][waf_index]
                        # word_to_shift = line.word["text"][waf_index + 1]

                        # shift content
                        indexs = line.word["UID"][waf_index][-1]

                        start = line.data["word_match"].index(waf_index + 1)
                        end = start + wc_substraction_count
                        line.update_stuff_at(start, end, waf_index, indexs)

                        # delete content
                        start_del = start - wc_substraction_count
                        end_del = start
                        line.delete_stuff_at(start_del, end_del)


                # mark the current and next feature space as processed
                words_and_feats[waf_index][1][0].append(self.WordColumnFeats.FEATURE_WAS_PROCESSED)
                words_and_feats[waf_index + 1][1][0].append(self.WordColumnFeats.FEATURE_WAS_PROCESSED)

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


    # todo factor this to other function
    class WordColumnFeats:
        FEATURE_WAS_PROCESSED ="processed"
        ONLY_WILDCARDS = 0
        ONLY_SPACES = 1
        ALL_SAME_CONTENT = 2
        MOSTLY_WILDCARDS = 3
        MOSTLY_SIMILAR_WORDS = 4
        MOSTLY_SAME_WORDS = 5
        WILDCARDS_LEFT = 6
        WILDCARDS_RIGHT = 7
        HIGH_WILDCARD_RATIO_IN_ONE_ITEM = 8
        HIGH_WILDCARD_RATIO_IN_MOST_ITEMS = 9

        


    def get_word_column_feats(self, word1, word2, word3, wildcard_character):
        from n_dist_keying.n_distance_voter import NDistanceVoter

        detected_feats = []

        words_input = [word1, word2, word3]
        counters_with_chars = {}
        counters_wildcard_streaks = []
        counter_only_wildcard_words = 0
        counter_only_spaces = 0
        counter_only_nones = 0
        last_word_index = -1
        last_wildcard_or_space_index = -1


        for word_index, word in enumerate(words_input):
            if word is None:
                counter_only_nones+=1
                continue

            # obtain longest character streak
            word_as_list = list(word)
            longest_wildcard_streak = 0
            streak_broke = False
            streak_is_lefthanded = True
            for char_index, char in enumerate(word_as_list):
                if streak_broke and char == wildcard_character:
                    streak_broke = False
                    longest_wildcard_streak = 0 # reset streak
                if char == wildcard_character:
                    longest_wildcard_streak+=1
                if char != wildcard_character:
                    streak_broke = True
                if char_index == len(word_as_list)-1 and \
                    char == wildcard_character:
                        streak_is_lefthanded = False
            if len(word_as_list) >= 1:
                wildcard_ratio = longest_wildcard_streak / len(word_as_list)
            else:
                wildcard_ratio = 0

            counters_wildcard_streaks.append((longest_wildcard_streak, wildcard_ratio, streak_is_lefthanded))

            word_only_wildcard = len(word.replace(wildcard_character, "")) == 0 and len(word) >= 1
            word_only_space = len(word.replace(" ","")) == 0 and len(word) >= 1

            if word_only_wildcard:
                counter_only_wildcard_words += 1
                last_wildcard_or_space_index = word_index
            elif word_only_space:
                counter_only_spaces += 1
                last_wildcard_or_space_index = word_index
            else:
                last_word_index = word_index
                if not word in counters_with_chars.keys():
                    counters_with_chars.update({word: 1})
                else:
                    counters_with_chars[word] += 1

        #for key in counters_with_chars.keys():
        #    value = counters_with_chars[key]



        ndist_voter = NDistanceVoter(counters_with_chars.keys())
        ndist_index = ndist_voter.compare_texts(take_longest_on_empty_lines=True)

        #ndist_result = words_input[ndist_index]
        #ndist_only_wildcard = len(ndist_result.replace(wildcard_character,"")) and len(ndist_result)>=1

        #other_word_index = None
        #if n_dist_only_wildcard:
        #    if column_item != None:
        #        if column_item != self._wildcard_character and \
        #                column_item != " ":
        words_are_similar = False
        counter_similar_words = 0
        counter_same_words = 0
        if len(counters_with_chars.keys()) >= 2:
            acc_vals = 0
            for key in ndist_voter.d_storage.key_val_dict:
                value = ndist_voter.d_storage.key_val_dict[key]
                acc_vals += value
                if value <= 0.18:
                    counter_similar_words += 1
            #average_dist_between_words = acc_vals / len(ndist_voter.d_storage.key_val_dict)
            #print("asd")
            #if average_dist_between_words <= 0.35:
            #    words_are_similar = True
        if len(counters_with_chars.keys()) == 1:
            key, value = counters_with_chars.popitem()
            counter_same_words = value

        high_wildcard_ratio_count = 0
        wildcards_mostly_left_indicator = 0
        other_than_wildcard_index = -1
        only_wildcard_index = -1
        for row_index, row in enumerate(counters_wildcard_streaks):
            wildcard_ratio = row[1]
            wildcards_left = row[2]
            if wildcard_ratio >= 0.40:
                only_wildcard_index = row_index
                high_wildcard_ratio_count += 1
                if wildcards_left:
                    wildcards_mostly_left_indicator += 1
                else:
                    wildcards_mostly_left_indicator -= 1
            else:
                other_than_wildcard_index = row_index


        high_ratio = False
        return_index = -1
        if high_wildcard_ratio_count==1:
            high_ratio = True
            return_index = only_wildcard_index
            detected_feats.append(self.WordColumnFeats.HIGH_WILDCARD_RATIO_IN_ONE_ITEM)
        if high_wildcard_ratio_count == len(words_input)-1:
            high_ratio = True
            return_index = other_than_wildcard_index
            detected_feats.append(self.WordColumnFeats.HIGH_WILDCARD_RATIO_IN_MOST_ITEMS)
        if high_ratio:
            if wildcards_mostly_left_indicator<0:
                detected_feats.append(self.WordColumnFeats.WILDCARDS_RIGHT)
            if wildcards_mostly_left_indicator >0:
                detected_feats.append(self.WordColumnFeats.WILDCARDS_LEFT)


        print(counters_wildcard_streaks)
        print("input:", words_input)
        print("output:", (detected_feats, return_index))
        #if "Dr." in words_input[0]:
        #    print("asd")

        return (detected_feats, return_index, counters_wildcard_streaks)

        """
        return_obj = None

        # return properties
        if counter_only_wildcard_words >= len(words_input):
            detected_feats.append(self.WordColumnFeats.ONLY_WILDCARDS)
            return_obj = (detected_feats, -1)
        elif counter_only_spaces >= len(words_input):
            detected_feats.append(self.WordColumnFeats.ONLY_SPACES)
            return_obj = (detected_feats, -1)
        elif counter_only_wildcard_words == len(words_input)-1:
            detected_feats.append(self.WordColumnFeats.MOSTLY_WILDCARDS)
            return_obj = (detected_feats, last_word_index)
        elif counter_similar_words == len(words_input)-1:
            detected_feats.append(self.WordColumnFeats.MOSTLY_SIMILAR_WORDS)
            return_obj = (detected_feats, last_wildcard_or_space_index)
        elif counter_same_words == len(words_input) -1:
            detected_feats.append(self.WordColumnFeats.MOSTLY_SAME_WORDS)
            return_obj = (detected_feats, last_wildcard_or_space_index)
        else:
            return_obj = (detected_feats, -1)

        if "Dr." in words_input[0]:
            print("asd")
        print(counters_wildcard_streaks)
        print("input:", words_input)
        print("output:", return_obj)
        return return_obj   
        """