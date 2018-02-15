
from Bio import pairwise2
import faulthandler

faulthandler.enable()


#res_three_2_multi = pairwise2.align.globalxx("(Westf.), Grevener", "IIIIII(Westf.), Grevener") # works

#res_three_2_multi = pairwise2.align.globalxx("(Westf.), Grevener", "------(Westf.), Grevener") # works


#res_three_2_multi_1 = pairwise2.align.globalxx("(Westf.), Grevener", "------(Westf.), Grevener", gap_char="-") #works

#res_three_2_multi_2 = pairwise2.align.globalxx("(Westf.), Grevener", "------(Westf.), Grevener", gap_char="-") #works

#res_three_2_multi_3 = pairwise2.align.globalxx("(Westf.), Grevener", "------(Westf.), Grevener", gap_char="†") # works
#res_three_2_multi_3 = pairwise2.align.globalxx("(Westf.), Grevener", "€(Westf.), Grevener") # doesn't work


text_a = "(Westf.), Grevener"
text_b = "††††††(Westf.), Grevener"



def convert_string_to_unicode_list(text):
    unicode_a= []
    for char in list(text):
        #echar = char.encode('UTF-16')
        ordinal = ord(char)
        unicode_a.append(ordinal)
    return unicode_a

def  convert_unicodelist_to_string(u_list):
    text = ""
    for number in list(u_list):
        #echar = char.encode('UTF-16')
        character = chr(number)
        text += character
    return text


text_a_uc_list = convert_string_to_unicode_list(text_a)
text_a_re_string = convert_unicodelist_to_string(text_a_uc_list)
text_b_uc_list = convert_string_to_unicode_list(text_b)
text_b_re_string = convert_unicodelist_to_string(text_b_uc_list)
gap_char_unicode = convert_string_to_unicode_list('†')


res_unicode = pairwise2.align.globalxx(text_a_uc_list, text_b_uc_list, gap_char=gap_char_unicode)  # doesn't work
result1_str = convert_unicodelist_to_string(res_unicode[0][0])
result2_str = convert_unicodelist_to_string(res_unicode[0][1])

res_three_2_multi_3 = pairwise2.align.globalxx("(Westf.), Grevener", "††††††(Westf.), Grevener") # doesn't work




res_three_2_multi = pairwise2.align.globalxx("(Westf.), Grevener", "¦¦¦¦¦¦(Westf.), Grevener")  # doesn't work



res_three_2_multi_3 = pairwise2.align.globalxx("(Westf.), Grevener", "††††††(Westf.), Grevener", gap_char="†")




#this is the isolated issue: produces Process finished with exit code 139 (interrupted by signal 11: SIGSEGV)
res_three_2_multi = pairwise2.align.globalxx("(Westf.), Grevener", "¦¦¦¦¦¦(Westf.), Grevener", gap_char='¦', force_generic=False)
print("asd")