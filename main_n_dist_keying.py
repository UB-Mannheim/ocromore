"""
   This is the starting file for comparing hocr-files to each other
   files are loaded to python-objects here and are then compared
   with different methods. One of them is the n-dist-keying
"""

from n_dist_keying.hocr_line_normalizer import HocrLineNormalizer
from n_dist_keying.hocr_bbox_comparator import HocrBBoxComparator
from n_dist_keying.hocr_line_height import LineHeightCalculator
from ocr_validation.ocr_validator import OCRvalidator




# Get lists of Hocr-objects from testfiles
hocr_comparator = HocrBBoxComparator()
ocrolist = hocr_comparator.get_ocropus_boxes("../Testfiles/oneprof_ocropus.html")
tesslist = hocr_comparator.get_tesseract_boxes("../Testfiles/oneprof_tesseract.html")
# abbylist = hocr_comparator.get_abbyy_boxes("../Testfiles/oneprof_abbyy.hocr.html")
abbylist = hocr_comparator.get_abbyy_boxes("../Testfiles/oneprof_abbyy_tables_ok.hocr.html")

#todo: Possibility calculate linefeed with additional information in unnormalized boxes


# Normalize list results for comparison
hocr_normalizer = HocrLineNormalizer()
ocrolist_normalized = hocr_normalizer.normalize_ocropus_list(ocrolist)
abbylist_normalized = hocr_normalizer.normalize_abbyy_list(abbylist)
tesslist_normalized = hocr_normalizer.normalize_tesseract_list(tesslist)

print("List results:---------------")
print("ocrolist_normalized.length: ", len(ocrolist_normalized))
print("tesslist.length: ", len(tesslist_normalized))
print("abbyylist.length: ", len(abbylist_normalized))

# Calculate line height in files, used for making linebreaks in merged ocr-output # todo get for pages
lh_calculator = LineHeightCalculator()
nldist_ocro, nlgap_ocro, nlh_ocro, ny_gaps_len_ocro, nlh_len_ocro = lh_calculator.calculate_line_distance_information(ocrolist_normalized)
nldist_tess, nlgap_tess, nlh_tess, ny_gaps_len_tess, nlh_len_tess  = lh_calculator.calculate_line_distance_information(tesslist_normalized)
nldist_abbyy, nlgap_abbyy, nlh_abbyy, ny_gaps_len_abbyy, nlh_len_abbyy = lh_calculator.calculate_line_distance_information(abbylist_normalized)




# Show a basic list comparison, with characterwise comparison (depreciated)
# hocr_comparator.compare_lists(ocrolist_normalized, tesslist, abbylist)
#exit(0)

# Prepare a basic list object with all ocr's which should be compared
base_ocr_lists = []
base_ocr_lists.append(abbylist_normalized)
base_ocr_lists.append(tesslist_normalized)
base_ocr_lists.append(ocrolist_normalized)

# Do the actual comparison of ocr lists, this matches lines with the same y-position together and calls them sets
ocr_comparison = hocr_comparator.compare_lists(base_ocr_lists)
ocr_comparison.sort_set()           #sort the created set after the y-height in ocr-documents
print("Print mean||decision||abbyy||tesseract||ocropus|||| without unspacing-------------------")
ocr_comparison.print_sets(False)
# todo possible: add substitution for characters, todo segmentate stuff
ocr_comparison.unspace_list(2, 1) # unspace ocropus with tesseract as unspacing template
ocr_comparison.unspace_list(0, 1) # unspace abbyy with tesseract as unspacing template
print("Print mean||decision||abbyy||tesseract||ocropus|||| ocropus and abbyy unspaced--------------------")
ocr_comparison.print_sets(False)



ocr_comparison.print_sets(True)     #print the sets created
ocr_comparison.do_n_distance_keying()   #do the keying, which makes the decision which is the best line for each set
ocr_comparison.print_n_distance_keying_results()  #print keying results
ocr_comparison.print_sets(False)    # print the sets again with decision information


ocr_comparison.save_n_distance_keying_results_to_file("./Testfiles/oneprof_keying_result.txt")

# Do steps to validate the used keying
ocr_validator = OCRvalidator()

ignore_linefeed = True
ignore_whitespace = False
"""
ocr_validator.set_groundtruth("./Testfiles/oneprof.gt.txt")
ocr_validator.set_ocr_file("./Testfiles/oneprof_keying_result.txt")
ocr_validator.compare_difflib_differ(ignore_linefeed, ignore_whitespace)
ocr_validator.set_ocr_file("./Testfiles/oneprof_abbyy.txt")
ocr_validator.compare_difflib_differ(ignore_linefeed, ignore_whitespace)
ocr_validator.set_ocr_file("./Testfiles/oneprof_tesseract_questionmark.txt")
ocr_validator.compare_difflib_differ(ignore_linefeed, ignore_whitespace, True)
"""
ocr_validator.set_groundtruth("./Testfiles/oneprof.gt.txt")
ocr_validator.set_ocr_file("./Testfiles/oneprof_keying_result.txt")
ocr_validator.compare_ocrolib_edist(ignore_linefeed, ignore_whitespace)
ocr_validator.set_ocr_file("./Testfiles/oneprof_abbyy.txt")
ocr_validator.compare_ocrolib_edist(ignore_linefeed, ignore_whitespace)
ocr_validator.set_ocr_file("./Testfiles/oneprof_tesseract_questionmark.txt")
ocr_validator.compare_ocrolib_edist(ignore_linefeed, ignore_whitespace)

# todo implement proper error rating against ground-truth
# todo implement difference matching
