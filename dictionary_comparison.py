"""
At the moment contains possibilities for dictionary comparison
"""
import difflib



my_dict = ["hello","hel1o","hallo","helau"]

def get_closest_match(text):

    TRESHOLD =0.4

    list_of_matches = difflib.get_close_matches(text,my_dict)

    final_list =  []
    for element in list_of_matches:
        seq_match = difflib.SequenceMatcher(None, element, text, True)
        mb_t = seq_match.get_matching_blocks()
        ratio = seq_match.ratio()
        if ratio>=0.4:
            final_list.append([element,ratio])


    # sort after ratio

    def take_second(elem):
        sec = elem[1]
        return sec


    sorted_list = sorted(final_list, key=take_second, reverse=True)
    #return first element
    return sorted_list[0]

closest_match = get_closest_match("he11o")
