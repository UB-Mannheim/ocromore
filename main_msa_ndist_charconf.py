from utils.df_objectifier import DFObjectifier
from pathlib import Path
from n_dist_keying.database_handler import DatabaseHandler
from utils.pycharm_handler import PycharmHandler
from ocr_validation.isri_handler import IsriHandler
import importlib
from configuration.configuration_handler import ConfigurationHandler



CODED_CONFIGURATION_PATH = './configuration/config_debug_js.conf'  # configuration which is not given with cli args

config_handler = ConfigurationHandler(first_init=True, fill_unkown_args=True, \
                                      coded_configuration_path=CODED_CONFIGURATION_PATH)
#config_handler = ConfigurationHandler() # initialization in subclass

config = config_handler.get_config()



# Functional Code: ...

dbdir_abs = 'sqlite:///' + str(Path(config.DB_DIR).absolute())

dataframe_wrapper = DFObjectifier(dbdir_abs + '/1957.db', '0237_1957_hoppa-405844417-0050_0290')
database_handler = DatabaseHandler(dataframe_wrapper, config.NUMBER_OF_INPUTS)
ocr_comparison = database_handler.create_ocr_comparison()
ocr_comparison.sort_set()
print("Print mean||decision||abbyy||tesseract||ocropus|||| without unspacing-------------------")
ocr_comparison.print_sets(False)


if config.DO_N_DIST_KEYING:
    print("Doing: N_DIST_KEYING, WORDWISE KEYING: ", config.NDIST_USE_WORDWISE_KEYING)
    ocr_comparison.do_n_distance_keying(config.NDIST_USE_WORDWISE_KEYING)   # do the keying, which makes the decision which is the best line for each set
    #ocr_comparison.print_n_distance_keying_results()  # print keying results
    if config.KEYING_RESULT_POSTCORRECTION:
        print("Doing: KEYING_RESULT_POSTCORRECTION")
        ocr_comparison.do_postcorrection(True)


    ocr_comparison.save_n_distance_keying_results_to_file(config.FILEPATH_NDIST_RESULT, config.NDIST_MODE_ADD_LINEBREAKS)

if config.DO_MSA_BEST:

    if config.MSA_BEST_USE_WORDWISE_MSA:
        # this is the new msa best invocation
        ocr_comparison.do_msa_best_new(config.MSA_BEST_USE_N_DIST_PIVOT, config.MSA_BEST_USE_LONGEST_PIVOT, config.MSA_BEST_USE_CHARCONFS, \
                                       config.MSA_BEST_USE_WORDWISE_MSA, config.MSA_BEST_USE_SEARCHSPACE)
    else:
        #todo refactor this old stuff
        if config.MSA_BEST_USE_CHARCONFS is False:
            if config.MSA_BEST_USE_N_DIST_PIVOT:
                print("Doing: DO_MSA_BEST with MSA_BEST_USE_N_DIST_PIVOT")

                ocr_comparison.do_msa_best_with_ndist_pivot()
            else:
                print("Doing: DO_MSA_BEST without NDIST_PIVOT")
                ocr_comparison.do_msa_best()
        else:
            if config.MSA_BEST_USE_N_DIST_PIVOT:
                print("Doing: DO_MSA_BEST with MSA_BEST_USE_N_DIST_PIVOT and CHARCONFS")

                ocr_comparison.do_msa_best_with_ndist_pivot_charconf()
            else:
                print("Doing: DO_MSA_BEST without NDIST_PIVOT and CHARCONFS")
                print("This is not implemented yet")


    #ocr_comparison.print_msa_best_results()
    ocr_comparison.save_dataset_to_file(config.FILEPATH_MSA_BEST_RESULT, 0, config.MODE_ADD_LINEBREAKS, "msa_best")

ocr_comparison.print_sets(False)


if config.DO_ISRI_VAL is True:
    isri_handler = IsriHandler()

    # Test 'accuracy'
    isri_handler.accuracy(config.FILEPATH_GROUNDTRUTH, config.FILEPATH_NDIST_RESULT, config.FILEPATH_ACCURACY_REPORT_NDIST)
    isri_handler.accuracy(config.FILEPATH_GROUNDTRUTH, config.FILEPATH_MSA_BEST_RESULT, config.FILEPATH_ACCURACY_REPORT_MSA)

    # Test 'wordacc'
    isri_handler.wordacc(config.FILEPATH_GROUNDTRUTH, config.FILEPATH_NDIST_RESULT, None, config.FILEPATH_WACCURACY_REPORT_NDIST)
    isri_handler.wordacc(config.FILEPATH_GROUNDTRUTH, config.FILEPATH_MSA_BEST_RESULT, None, config.FILEPATH_WACCURACY_REPORT_MSA)

if config.DISPLAY_DIFFERENCES:
    pyc_handler = PycharmHandler()
    pyc_handler.show_file_comparison(config.FILEPATH_GROUNDTRUTH, config.FILEPATH_NDIST_RESULT)
    pyc_handler.show_file_comparison(config.FILEPATH_GROUNDTRUTH, config.FILEPATH_MSA_BEST_RESULT)

    #testing strange wordaccuracy report production
    #pyc_handler.show_file_comparison(FILEPATH_NDIST_RESULT, FILEPATH_MSA_BEST_RESULT)
    #pyc_handler.show_file_comparison(FILEPATH_WACCURACY_REPORT_NDIST, FILEPATH_WACCURACY_REPORT_MSA)