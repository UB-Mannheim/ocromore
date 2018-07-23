from multi_sequence_alignment.msa_handler import MsaHandler
from akf_corelib.typecasts import TypeCasts

text_A = '" 1953 6 %'
text_B = 'II 1953 60 %'

text_A = '¦sulllt)lhill ===-----'
text_B = '¦SÜQÜJESIFHLEH falb) Geisweid'

text_A = '¦sullltlhill'
text_B = '¦SÜQÜJESIFHLEH falb) Geisweid'


def add_gapchar_at_start(text, wildcard_character='¦'):
    return wildcard_character+text



text_1_uclist = TypeCasts.convert_string_to_unicode_list(text_A)
text_1_string = TypeCasts.convert_unicodelist_to_string(text_1_uclist)


#text_A = add_gapchar_at_start(text_A)
#text_B = add_gapchar_at_start(text_B)
print("inp1", text_A)
print("inp2", text_B)

msa_handler = MsaHandler()
text_Ab, text_Ba = msa_handler.pairwise_unicode(text_A,text_B)

print("res1",text_Ab)
print("res2",text_Ba)