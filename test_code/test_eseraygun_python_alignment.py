
import inspect


def msa_alignment_skbio(text_1, text_2, text_3):
    from skbio.alignment import  global_pairwise_align, make_identity_substitution_matrix

    from multi_sequence_alignment.scikit_custom_sequence_ocr import CustomSequence


    #
    gap_open_penalty = 1
    gap_extend_penalty = 1
    # substitution_matrix_b50 =CustomSequence.blosum50 # just an example

    try:
        """    
        alignment, score, start_end_positions = local_pairwise_align_ssw(
            DNA("ACTAAGGCTCTCTACCCCTCTCAGAGA"),
            DNA("ACTAAGGCTCCTAACCCCCTTTTCTCAGA")
        )
        """
        # todo sequence/_sequence.py is missing proper encoding, this has to fix to make this work completely atm workaround: replace non ascii with '?'
        # also sequence/_grammared_sequence.py
        # cs1 = CustomSequence("Hallo das ist ein Test überkrass")
        # cs2 = CustomSequence("H4llo das ist Test überkraass")
        cs1 = CustomSequence(text_1)
        cs2 = CustomSequence(text_2)
        cs3 = CustomSequence(text_3)

        # substitution_matrix_unity = cs2.create_unity_sequence_matrix()
        substitution_matrix_equal = make_identity_substitution_matrix(1 ,-1 ,cs2.create_charset_string())

        # alignment, score, start_end_positions = local_pairwise_align(cs1, cs2, gap_open_penalty, gap_extend_penalty, substitution_matrix_unity)

        alignment12, score12, start_end_positions12 = global_pairwise_align(cs1, cs2, gap_open_penalty, gap_extend_penalty, substitution_matrix_equal)
        alignment23, score23, start_end_positions23 = global_pairwise_align(cs2, cs3, gap_open_penalty, gap_extend_penalty, substitution_matrix_equal)

        # alignment3, score3, start_end_positions3 = global_pairwise_align("Hallo das ist ein Test", "H4llo das ist Test", gap_open_penalty, gap_extend_penalty, substitution_matrix_equal)
        # res_one_1, res_two_1 = MsaHandler.compare(list_one, list_two)

        # res_two_2, res_three_2 = MsaHandler.compare(list_two, list_three)
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

        res_one_1_filled = "test"#MsaHandler.fillup_wildcarded_result(res_one_1, pivot_msa, '@')
        res_three_2_filled = "test"# MsaHandler.fillup_wildcarded_result(res_three_2, pivot_msa, '@')

        res_final_1 = res_one_1_filled
        res_final_2 = pivot_msa
        res_final_3 = res_three_2
        #res_final_3 = res_three_2_filled
        return res_final_1, res_final_2, res_final_3


    except Exception as ex:
        tr = inspect.trace()
        print("Exception raised in %s" % tr[-1][3])






















import nwalign3 as nw
reto = nw.global_align("CEELECANTH", "PELICAN")
reto2 = nw.global_align("(Westf.), Grevener", "††††††(Westf.), Grevener")
reto3 = nw.global_align("(Westf.), Grevener", "††††††(Westf.), Grevener",gap_open=-5, gap_extend=-2)



#import seqanpy
#print(seqanpy.align_global('ACCGGT', 'CCG'))



from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner

# Create sequences to be aligned.
a = Sequence('what a beautiful day'.split())
b = Sequence('what a disappointingly bad day'.split())

a = Sequence("(Westf.), Grevener".split())
b = Sequence("††††††(Westf.), Grevener".split())
# Create a vocabulary and encode the sequences.
v = Vocabulary()
aEncoded = v.encodeSequence(a)
bEncoded = v.encodeSequence(b)

# Create a scoring and align the sequences using global aligner.
scoring = SimpleScoring(2, -1)
aligner = GlobalSequenceAligner(scoring, -2)
score, encodeds = aligner.align(aEncoded, bEncoded, backtrace=True)

# Iterate over optimal alignments and print them.
for encoded in encodeds:
    alignment = v.decodeSequenceAlignment(encoded)
    print(alignment)
    print('Alignment score:', alignment.score)
    print('Percent identity:', alignment.percentIdentity())