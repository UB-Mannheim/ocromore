from multi_sequence_alignment.msa_algorithm import MultiSequenceAlignment
import numpy as np
import inspect
from Bio import pairwise2
from Bio.SubsMat import MatrixInfo as matlist


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
    def msa_alignment_gonzalo(text_1, text_2, text_3):
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
        return res_final_1, res_final_2, res_final_3

    @staticmethod
    def msa_alignment_skbio(text_1, text_2, text_3):
        from skbio import TabularMSA, DNA
        from skbio.sequence import GrammaredSequence
        from skbio.alignment import local_pairwise_align_ssw, local_pairwise_align, global_pairwise_align, make_identity_substitution_matrix

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
            #res_one_1, res_two_1 = MsaHandler.compare(list_one, list_two)

            #res_two_2, res_three_2 = MsaHandler.compare(list_two, list_three)
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

            print(len(res_one_1), res_one_1)
            print(len(pivot_msa), pivot_msa)
            print(len(res_three_2), res_three_2)
            # if res_one_1.__contains__("Sitz:") is True:
            #    print("asd")

            res_one_1_filled = MsaHandler.fillup_wildcarded_result(res_one_1, pivot_msa, '@')
            res_three_2_filled = MsaHandler.fillup_wildcarded_result(res_three_2, pivot_msa, '@')

            res_final_1 = res_one_1_filled
            res_final_2 = pivot_msa
            # res_final_3 = res_three_2
            res_final_3 = res_three_2_filled
            return res_final_1, res_final_2, res_final_3


        except Exception as ex:
            tr = inspect.trace()
            print("Exception raised in %s" % tr[-1][3])

    @staticmethod
    def msa_alignment_biopython(text_1, text_2, text_3,wildcard_character='¦'):
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
        wildcard_character = '@'
        # http://biopython.org/DIST/docs/api/Bio.pairwise2-module.html

        #matrix = matlist.blosum62


        points_identical_char = 2
        penality_non_identical_char = -1
        penalty_opening_gap = -0.5
        penalty_extending_gap  = -0.1

        take_first_or_last = True  # True take first alignment, False take last alignment

        try:
            alignment12_multi = pairwise2.align.globalms(text_1, text_2,points_identical_char,penality_non_identical_char,penalty_opening_gap,penalty_extending_gap, gap_char=wildcard_character,penalize_end_gaps=False)
            alignment23_multi = pairwise2.align.globalms(text_2, text_3,points_identical_char,penality_non_identical_char,penalty_opening_gap,penalty_extending_gap, gap_char=wildcard_character,penalize_end_gaps=False)
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

            res_one_1 = str(alignment12[0])
            res_two_1 = str(alignment12[1])
            res_two_2 = str(alignment23[0])
            res_three_2 = str(alignment23[1])

            list_res_one_1 = list(res_one_1)
            list_res_two_1 = list(res_two_1)

            list_res_two_2 = list(res_two_2)
            list_res_three_2 = list(res_three_2)

            list_pivot_msa = None
            pivot_msa = None

            pivot_index = -1
            if len(list_res_two_1) >= len(list_res_two_2):
                # if len(list_res_two_1) > len(list_res_two_2):
                list_pivot_msa = list_res_two_1
                pivot_msa = res_two_1
                pivot_index = 0
            else:
                list_pivot_msa = list_res_two_2
                pivot_msa = res_two_2
                pivot_index = 1
            print(len(res_one_1), res_one_1)
            print(len(pivot_msa), pivot_msa)
            print(len(res_three_2), res_three_2)
            # if res_one_1.__contains__("Sitz:") is True:
            #    print("asd")

            USE_OLD_FILLING = False
            if USE_OLD_FILLING is True:
                res_one_1_filled = MsaHandler.fillup_wildcarded_result(res_one_1, pivot_msa)
                res_three_2_filled = MsaHandler.fillup_wildcarded_result(res_three_2, pivot_msa)
            else:

                if pivot_index == 0:

                    res_three_2_cp = res_one_1[:]
                    pivot_msa_cp = pivot_msa[:]
                    res_three_2_multi = pairwise2.align.globalxx(res_three_2_cp, pivot_msa_cp, gap_char=wildcard_character, force_generic=True)

                    res_one_1_filled = res_one_1
                    res_three_2_filled = res_three_2_multi[0][0]
                elif pivot_index == 1:

                    #res_one_1_multi = pairwise2.align.globalms(res_one_1, pivot_msa, points_identical_char,
                    #                                             penality_non_identical_char, penalty_opening_gap,
                    #                                             penalty_extending_gap, gap_char='¦',
                    #                                             penalize_end_gaps=False)

                    res_one_1_cp = res_one_1[:]
                    pivot_msa_cp = pivot_msa[:]
                    res_one_1_multi = pairwise2.align.globalxx(res_one_1_cp,pivot_msa_cp, gap_char=wildcard_character, force_generic=True)
                    res_one_1_filled = res_one_1_multi[0][0]
                    res_three_2_filled = res_three_2




            res_one_1_filledOld = MsaHandler.fillup_wildcarded_result(res_one_1, pivot_msa, '¦')
            res_three_2_filledOld = MsaHandler.fillup_wildcarded_result(res_three_2, pivot_msa, '¦')

            res_final_1 = res_one_1_filled
            res_final_2 = pivot_msa
            # res_final_3 = res_three_2
            res_final_3 = res_three_2_filled
            print("j4t-new")
            print(res_final_1)
            print(res_final_2)
            print(res_final_3)
            print("j4t-old")
            print(res_one_1_filledOld)
            print(res_final_2)
            print(res_three_2_filledOld)
            return res_final_1, res_final_2, res_final_3

        except Exception as ex:
            print(ex)

        print("My Alignment Test ----")
        #print(pairwise2.format_alignment(*alignmentsPW[0]))
        #print(pairwise2.format_alignment(*alignmentsPW[1]))



        # alignment3, score3, start_end_positions3 = global_pairwise_align("Hallo das ist ein Test", "H4llo das ist Test", gap_open_penalty, gap_extend_penalty, substitution_matrix_equal)
        # res_one_1, res_two_1 = MsaHandler.compare(list_one, list_two)

        # res_two_2, res_three_2 = MsaHandler.compare(list_two, list_three)


    @staticmethod
    def get_best_of_three(text_1, text_2, text_3):

        PRINT_RESULTS = True
        MODE_GONZALO = 'gonzalo'
        MODE_SKBIO = 'scikit-bio_alignment'
        MODE_BIOPYTHON = 'biopython'
        MODE = MODE_BIOPYTHON

        if MODE == MODE_GONZALO:
            res_final_1, res_final_2, res_final_3 = MsaHandler.msa_alignment_gonzalo(text_1, text_2, text_3)
            wildcard_character = '¦'
        elif MODE == MODE_SKBIO:
            res_final_1, res_final_2, res_final_3 = MsaHandler.msa_alignment_skbio(text_1, text_2, text_3)
            wildcard_character = '@'
        elif MODE == MODE_BIOPYTHON:
            wildcard_character = '¦'
            res_final_1, res_final_2, res_final_3 = MsaHandler.msa_alignment_biopython(text_1, text_2, text_3, wildcard_character)


        # This is the voting algorithm -
        best, best_stripped = MsaHandler.best_of_three_simple(res_final_1, res_final_2, res_final_3, 1,wildcard_character)  # res two is the best element
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
            print("A:",res_final_1)
            print("B:",res_final_2)
            print("C:",res_final_3)
            print("D:", best)
            print("E:", best_stripped)
            print("F:", best_stripped_non_multi_whitespace)
        return best_stripped_non_multi_whitespace