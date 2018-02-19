from utils.df_objectifier import DFObjectifier
from pathlib import Path
from n_dist_keying.database_handler import DatabaseHandler
from ocr_validation.ocr_validator import OCRvalidator
from utils.pycharm_handler import PycharmHandler
from ocr_validation.isri_handler import IsriHandler

DB_DIR = './Testfiles/sql/'
NUMBER_OF_INPUTS = 3  # number of ocr inputs which will be compared, todo make this dynmically with maxlen or smth
# keying mechanism
DO_N_DIST_KEYING = True
DO_WORDWISE_KEYING = False
DO_MSA_BEST = False

# Settings for Multi Sequence Alignment Best
MSA_BEST_USE_N_DIST_PIVOT = True

# postcorrection settings:
KEYING_RESULT_POSTCORRECTION = True

# validation settings:
IGNORE_LINEFEED = False
IGNORE_WHITESPACE = False
DISPLAY_DIFFERENCES = True
DO_ISRI_VAL = False


#Filenames
FILEPATH_MSA_BEST_RESULT = "./Testfiles/dbprof_msa_best_result.txt"
FILEPATH_NDIST_RESULT    = "./Testfiles/dbprof_ndist_result.txt"
FILEPATH_GROUNDTRUTH = "./Testfiles/dbprof.gt.txt"

FILEPATH_ACCURACY_REPORT_MSA = "./Testfiles/isri_accreport_msa_best_dbprof.txt"
FILEPATH_ACCURACY_REPORT_NDIST = "./Testfiles/isri_accreport_ndist_keying_dbprof.txt"
FILEPATH_WACCURACY_REPORT_MSA = "./Testfiles/isri_waccreport_msa_best_dbprof.txt"
FILEPATH_WACCURACY_REPORT_NDIST = "./Testfiles/isri_waccreport_ndist_keying_dbprof.txt"


# Functional Code: ...

dbdir_abs = 'sqlite:///' + str(Path(DB_DIR).absolute())

dataframe_wrapper = DFObjectifier(dbdir_abs + '/1957.db', '0237_1957_hoppa-405844417-0050_0290')
database_handler = DatabaseHandler(dataframe_wrapper, NUMBER_OF_INPUTS)
ocr_comparison = database_handler.create_ocr_comparison()
ocr_comparison.sort_set()
print("Print mean||decision||abbyy||tesseract||ocropus|||| without unspacing-------------------")
ocr_comparison.print_sets(False)


if DO_N_DIST_KEYING:
    print("Doing: N_DIST_KEYING, WORDWISE KEYING: ",DO_WORDWISE_KEYING)
    ocr_comparison.do_n_distance_keying(DO_WORDWISE_KEYING)   # do the keying, which makes the decision which is the best line for each set
    #ocr_comparison.print_n_distance_keying_results()  # print keying results
    if KEYING_RESULT_POSTCORRECTION:
        print("Doing: KEYING_RESULT_POSTCORRECTION")
        ocr_comparison.do_postcorrection(True)

    MODE_ADD_LINEBREAKS = False #todo add linebreaks later!
    ocr_comparison.save_n_distance_keying_results_to_file(FILEPATH_NDIST_RESULT, MODE_ADD_LINEBREAKS)

if DO_MSA_BEST:
    if MSA_BEST_USE_N_DIST_PIVOT:
        print("Doing: DO_MSA_BEST with MSA_BEST_USE_N_DIST_PIVOT")

        ocr_comparison.do_msa_best_with_ndist_pivot()
    else:
        print("Doing: DO_MSA_BEST without NDIST_PIVOT")
        ocr_comparison.do_msa_best()
    MODE_ADD_LINEBREAKS = False #todo add linebreaks later!

    #ocr_comparison.print_msa_best_results()
    ocr_comparison.save_dataset_to_file(FILEPATH_MSA_BEST_RESULT, 0, MODE_ADD_LINEBREAKS, "msa_best")

ocr_comparison.print_sets(False)


if DO_ISRI_VAL is True:
    isri_handler = IsriHandler()

    # Test 'accuracy'
    isri_handler.accuracy(FILEPATH_GROUNDTRUTH, FILEPATH_NDIST_RESULT, FILEPATH_ACCURACY_REPORT_NDIST)
    isri_handler.accuracy(FILEPATH_GROUNDTRUTH, FILEPATH_MSA_BEST_RESULT, FILEPATH_ACCURACY_REPORT_MSA)

    # Test 'wordacc'
    isri_handler.wordacc(FILEPATH_GROUNDTRUTH, FILEPATH_NDIST_RESULT, None, FILEPATH_WACCURACY_REPORT_NDIST)
    isri_handler.wordacc(FILEPATH_GROUNDTRUTH, FILEPATH_MSA_BEST_RESULT, None, FILEPATH_WACCURACY_REPORT_MSA)

if DISPLAY_DIFFERENCES:
    pyc_handler = PycharmHandler()
    pyc_handler.show_file_comparison(FILEPATH_GROUNDTRUTH, FILEPATH_NDIST_RESULT)
    pyc_handler.show_file_comparison(FILEPATH_GROUNDTRUTH, FILEPATH_MSA_BEST_RESULT)

    #testing strange wordaccuracy report production
    #pyc_handler.show_file_comparison(FILEPATH_NDIST_RESULT, FILEPATH_MSA_BEST_RESULT)
    #pyc_handler.show_file_comparison(FILEPATH_WACCURACY_REPORT_NDIST, FILEPATH_WACCURACY_REPORT_MSA)