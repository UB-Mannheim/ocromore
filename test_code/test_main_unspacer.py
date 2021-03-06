"""
   This is the starting file for testing unspacing capabilities (was developed before msa_algorithm)
   generates unspaced and line height adapted files from different ocr
   results and compares them to ground truth
"""

from n_dist_keying.hocr_line_normalizer import HocrLineNormalizer
from n_dist_keying.hocr_bbox_comparator import HocrBBoxComparator
from n_dist_keying.hocr_line_height import LineHeightCalculator
from n_dist_keying.textfile_generator import TextFileGenerator
from ocr_validation.ocr_validator import OCRvalidator
from ocr_validation.visualization_handler import VisualizationHandler


USE_REFSPACING = True  # instead of unspacing algorithm use the respacing algorithm
DISPLAY_DIFFERENCES = True
IGNORE_LINEFEED = False
IGNORE_WHITESPACE = False


# base files (input)
filepath_ground_truth = "./Testfiles/oneprof.gt.txt"
filepath_ocropus = "../Testfiles/oneprof_ocropus.html"
filepath_tesseract = "../Testfiles/oneprof_tesseract_sure.html"
filepath_abbyy = "../Testfiles/oneprof_abbyy_tables_ok.hocr.html"
filepath_tesseract_txt = "./Testfiles/oneprof_tesseract_sure.txt"


# textfiles which get generated
filepath_ocropus_txt = "./Testfiles/oneprof_ocropus_spaced.txt" #ocropus without lhi adaption
filepath_abbyy_txt = "./Testfiles/oneprof_abbyy.txt"




filepath_ocropus_lha_txt = "./Testfiles/oneprof_ocropus_spaced_lha.txt"
filepath_abbyy_lha_txt = "./Testfiles/oneprof_abbyy_lha.txt"

# textfiles which get generated for final spacing comparison
filepath_ocropus_unspaced_lha = "./Testfiles/oneprof_ocropus_unspaced_lha.txt"
filepath_abbyy_unspaced_lha = "./Testfiles/oneprof_abbyy_unspaced_lha.txt"


hocr_comparator = HocrBBoxComparator()
ocrolist = hocr_comparator.get_ocropus_boxes(filepath_ocropus)
tesslist = hocr_comparator.get_tesseract_boxes(filepath_tesseract)
abbylist = hocr_comparator.get_abbyy_boxes(filepath_abbyy)

hocr_normalizer = HocrLineNormalizer()
ocrolist_normalized = hocr_normalizer.normalize_ocropus_list(ocrolist)
abbylist_normalized = hocr_normalizer.normalize_abbyy_list(abbylist)
tesslist_normalized = hocr_normalizer.normalize_tesseract_list(tesslist)
lh_calculator = LineHeightCalculator()

lhi_abbyy_normalized = lh_calculator.calculate_line_distance_information(abbylist_normalized, False, True, "abbyy_normalized")
lhi_tesseract_normalized = lh_calculator.calculate_line_distance_information(tesslist_normalized, False, True, "tesseract_normalized")
lhi_ocropus_normalized = lh_calculator.calculate_line_distance_information(ocrolist_normalized, False, True, "ocropus_normalized")



tfg = TextFileGenerator()
tfg.create_file(lhi_abbyy_normalized, abbylist_normalized, filepath_abbyy_lha_txt)

tfg2 = TextFileGenerator()
tfg2.create_file(lhi_ocropus_normalized, ocrolist_normalized, filepath_ocropus_lha_txt)


tfg3 = TextFileGenerator()
tfg3.create_file(None, ocrolist_normalized, filepath_ocropus_txt, False)

tfg4 = TextFileGenerator()
tfg4.create_file(None, abbylist_normalized, filepath_abbyy_txt, False)


base_ocr_lists = []
base_ocr_lists.append(abbylist_normalized)
base_ocr_lists.append(tesslist_normalized)
base_ocr_lists.append(ocrolist_normalized)
ocr_comparison = hocr_comparator.compare_lists(base_ocr_lists)
ocr_comparison.add_line_information(lhi_abbyy_normalized)
ocr_comparison.add_line_information(lhi_tesseract_normalized)
ocr_comparison.add_line_information(lhi_ocropus_normalized)
ocr_comparison.sort_set()
print("Print mean||decision||abbyy||tesseract||ocropus|||| without unspacing-------------------")
ocr_comparison.print_sets(False)
if not USE_REFSPACING:
    ocr_comparison.unspace_list(2, 1)  # unspace ocropus with tesseract as unspacing template
    ocr_comparison.unspace_list(0, 1)  # unspace abbyy with tesseract as unspacing template
else:
    ocr_comparison.refspace_list(2, 1)  # refspace ocropus with tesseract as reference spacing template
    ocr_comparison.refspace_list(0, 1)  # refspace abbyy with tesseract as reference spacing template


print("Print mean||decision||abbyy||tesseract||ocropus|||| ocropus and abbyy unspaced--------------------")
ocr_comparison.print_sets(False)

ocr_comparison.save_n_distance_keying_results_to_file("./Testfiles/oneprof_keying_result.txt", True)
ocr_comparison.save_dataset_to_file(filepath_ocropus_unspaced_lha, 2, True)
ocr_comparison.save_dataset_to_file(filepath_abbyy_unspaced_lha, 0, True)

ocr_validator = OCRvalidator()

print("Comparison of the unspaced files and spaced files to groundtruth--------------")
print("Refspacing is: ", USE_REFSPACING)
ocr_validator.set_groundtruth(filepath_ground_truth)
# plain file comparison
print("Plain file comparison---(tesseract is lha by default)--")
ocr_validator.set_ocr_file(filepath_ocropus_txt)
ocr_validator.compare_ocrolib_edist(IGNORE_LINEFEED, IGNORE_WHITESPACE)
ocr_validator.set_ocr_file(filepath_abbyy_txt)
ocr_validator.compare_ocrolib_edist(IGNORE_LINEFEED, IGNORE_WHITESPACE)
ocr_validator.set_ocr_file(filepath_tesseract_txt)
ocr_validator.compare_ocrolib_edist(IGNORE_LINEFEED, IGNORE_WHITESPACE)


# lha file comparison
print("LHA file comparison---(tesseract is lha by default)-------------")
ocr_validator.set_ocr_file(filepath_ocropus_lha_txt)
ocr_validator.compare_ocrolib_edist(IGNORE_LINEFEED, IGNORE_WHITESPACE)
ocr_validator.set_ocr_file(filepath_abbyy_lha_txt)
ocr_validator.compare_ocrolib_edist(IGNORE_LINEFEED, IGNORE_WHITESPACE)
ocr_validator.set_ocr_file(filepath_tesseract_txt)
ocr_validator.compare_ocrolib_edist(IGNORE_LINEFEED, IGNORE_WHITESPACE)

# unspaced + lha file comparsion

print("Unspaced + LHA file comparison---(tesseract is lha and us by default)-------------")

ocr_validator.set_ocr_file(filepath_ocropus_unspaced_lha)
ocr_validator.compare_ocrolib_edist(IGNORE_LINEFEED, IGNORE_WHITESPACE)
ocr_validator.set_ocr_file(filepath_abbyy_unspaced_lha)
ocr_validator.compare_ocrolib_edist(IGNORE_LINEFEED, IGNORE_WHITESPACE)
ocr_validator.set_ocr_file(filepath_tesseract_txt)
ocr_validator.compare_ocrolib_edist(IGNORE_LINEFEED, IGNORE_WHITESPACE)


if DISPLAY_DIFFERENCES:
    pyc_handler = VisualizationHandler()
    # the lha visual comparison
    #pyc_handler.show_file_comparison(filepath_ocropus_lha_txt, filepath_ocropus_txt)
    #pyc_handler.show_file_comparison(filepath_abbyy_lha_txt, filepath_abbyy_txt)
    pyc_handler.show_file_comparison(filepath_ground_truth, filepath_ocropus_unspaced_lha)
    # mind this is the line height adapted text, generated by this file
    pyc_handler.show_file_comparison(filepath_ground_truth, filepath_abbyy_unspaced_lha)
    #pyc_handler.show_file_comparison(filepath_ground_truth, filepath_abbyy_lha_txt)
    #pyc_handler.show_file_comparison(filepath_ground_truth, filepath_abbyy_unspaced_lha)
