"""
   This is the starting file for comparing hocr-files to each other
   files are loaded to python-objects here and are then compared
   with different methods. One of them is the n-dist-keying
"""

from n_dist_keying.hocr_line_normalizer import HocrLineNormalizer
from n_dist_keying.hocr_bbox_comparator import HocrBBoxComparator
from n_dist_keying.hocr_line_height import LineHeightCalculator
from n_dist_keying.textfile_generator import TextFileGenerator
from ocr_validation.ocr_validator import OCRvalidator
from utils.pycharm_handler import PycharmHandler


# Get lists of Hocr-objects from testfiles
hocr_comparator = HocrBBoxComparator()
ocrolist = hocr_comparator.get_ocropus_boxes("../Testfiles/oneprof_ocropus.html")
tesslist = hocr_comparator.get_tesseract_boxes("../Testfiles/oneprof_tesseract_sure.html")
# abbylist = hocr_comparator.get_abbyy_boxes("../Testfiles/oneprof_abbyy.hocr.html") #original abbyy tables
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

lhi_abbyy_normalized = lh_calculator.calculate_line_distance_information(abbylist_normalized, False, True, "abbyy_normalized")
lhi_tesseract_normalized = lh_calculator.calculate_line_distance_information(tesslist_normalized, False, True, "tesseract_normalized")
lhi_ocropus_normalized = lh_calculator.calculate_line_distance_information(ocrolist_normalized, False, True, "ocropus_normalized")


# Show a basic list comparison, with characterwise comparison (depreciated)
# hocr_comparator.compare_lists(ocrolist_normalized, tesslist, abbylist)
#exit(0)

export_adapted_abbyy_result = True
abbyy_text_file_path = "./Testfiles/oneprof_abbyy_result_lh_adapted.txt"
if export_adapted_abbyy_result:
    """
        Abbyy output comes only in html-hocr. Therefore the output has to be adapted.
        Some hocr-tools are used to create text https://github.com/tmbdev/hocr-tools
        (please check which exactly). They don't put in line feeds in text. So this
        utilizes the comparator to add some linefeeds (report this to converter-maintainers 
        if necessary)
    """
    tfg = TextFileGenerator()
    tfg.create_file(lhi_abbyy_normalized, abbylist_normalized, abbyy_text_file_path)


export_adapted_ocropus_result = True
ocropus_text_file_path = "./Testfiles/oneprof_ocropus_result_lh_adapted.txt"
if export_adapted_ocropus_result:
    tfg2 = TextFileGenerator()
    tfg2.create_file(lhi_ocropus_normalized, ocrolist_normalized, ocropus_text_file_path)



# Prepare a basic list object with all ocr's which should be compared
base_ocr_lists = []
base_ocr_lists.append(abbylist_normalized)
base_ocr_lists.append(tesslist_normalized)
base_ocr_lists.append(ocrolist_normalized)

# Do the actual comparison of ocr lists, this matches lines with the same y-position together and calls them sets
ocr_comparison = hocr_comparator.compare_lists(base_ocr_lists)
# add line information in the order the base ocr lists where appended
ocr_comparison.add_line_information(lhi_abbyy_normalized)
ocr_comparison.add_line_information(lhi_tesseract_normalized)
ocr_comparison.add_line_information(lhi_ocropus_normalized)
# sort the created set after the y-height in ocr-documents
ocr_comparison.sort_set()
print("Print mean||decision||abbyy||tesseract||ocropus|||| without unspacing-------------------")
ocr_comparison.print_sets(False)
# todo possible: add substitution for characters, todo segmentate stuff
#ocr_comparison.refspace_list(2, 1) # refspace ocropus with tesseract as unspacing template
ocr_comparison.unspace_list(2, 1) # unspace ocropus with tesseract as unspacing template
print("Print mean||decision||abbyy||tesseract||ocropus|||| ocropus and abbyy unspaced--------------------")
ocr_comparison.print_sets(False)



ocr_comparison.print_sets(True)     # print the sets created
ocr_comparison.do_n_distance_keying()   # do the keying, which makes the decision which is the best line for each set
ocr_comparison.print_n_distance_keying_results()  # print keying results
ocr_comparison.print_sets(False)    # print the sets again with decision information

ocr_comparison.save_n_distance_keying_results_to_file("./Testfiles/oneprof_keying_result.txt", True)

# Do steps to validate the used keying
ocr_validator = OCRvalidator()

ignore_linefeed = False
ignore_whitespace = False

ocr_validator.set_groundtruth("./Testfiles/oneprof.gt.txt")
ocr_validator.set_ocr_file("./Testfiles/oneprof_keying_result.txt")
ocr_validator.compare_ocrolib_edist(ignore_linefeed, ignore_whitespace)
ocr_validator.set_ocr_file("./Testfiles/oneprof_abbyy.txt")
ocr_validator.compare_ocrolib_edist(ignore_linefeed, ignore_whitespace)
ocr_validator.set_ocr_file(abbyy_text_file_path)
ocr_validator.compare_ocrolib_edist(ignore_linefeed, ignore_whitespace)
ocr_validator.set_ocr_file("./Testfiles/oneprof_tesseract_sure.txt")
ocr_validator.compare_ocrolib_edist(ignore_linefeed, ignore_whitespace)
ocr_validator.set_ocr_file(ocropus_text_file_path)
ocr_validator.compare_ocrolib_edist(ignore_linefeed, ignore_whitespace)

# show differences
display_differences = True
if display_differences:
    pyc_handler = PycharmHandler()
    pyc_handler.show_file_comparison("./Testfiles/oneprof.gt.txt", "./Testfiles/oneprof_keying_result.txt")
    # mind this is the line height adapted text, generated by this file
    pyc_handler.show_file_comparison("./Testfiles/oneprof.gt.txt", abbyy_text_file_path)
    pyc_handler.show_file_comparison("./Testfiles/oneprof.gt.txt", ocropus_text_file_path)
    pyc_handler.show_file_comparison("./Testfiles/oneprof.gt.txt", "./Testfiles/oneprof_tesseract_sure.txt")

# todo implement difference matching
