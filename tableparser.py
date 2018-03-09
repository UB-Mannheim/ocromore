from utils.df_objectifier import DFObjectifier
from n_dist_keying.database_handler import DatabaseHandler
from utils.pycharm_handler import PycharmHandler
from ocr_validation.isri_handler import IsriHandler


class TableParser(object):


    def __init__(self, config):
        print("asd")
        self._config = config

    def parse_a_table(self, dbdir_abs, table):

        dataframe_wrapper = DFObjectifier(dbdir_abs, table)
        database_handler = DatabaseHandler(dataframe_wrapper, self._config.NUMBER_OF_INPUTS)
        ocr_comparison = database_handler.create_ocr_comparison()
        ocr_comparison.sort_set()
        print("Print mean||decision||abbyy||tesseract||ocropus|||| without unspacing-------------------")
        ocr_comparison.print_sets(False)


        if self._config.DO_N_DIST_KEYING:
            print("Doing: N_DIST_KEYING, WORDWISE KEYING: ", self._config.NDIST_USE_WORDWISE_KEYING)
            ocr_comparison.do_n_distance_keying(self._config.NDIST_USE_WORDWISE_KEYING)   # do the keying, which makes the decision which is the best line for each set
            #ocr_comparison.print_n_distance_keying_results()  # print keying results
            if self._config.KEYING_RESULT_POSTCORRECTION:
                print("Doing: KEYING_RESULT_POSTCORRECTION")
                ocr_comparison.do_postcorrection(True)


            ocr_comparison.save_n_distance_keying_results_to_file(self._config.FILEPATH_NDIST_RESULT, self._config.NDIST_MODE_ADD_LINEBREAKS)

        if self._config.DO_MSA_BEST:

            if self._config.MSA_BEST_USE_WORDWISE_MSA:
                # this is the new msa best invocation
                ocr_comparison.do_msa_best_new(self._config.MSA_BEST_USE_N_DIST_PIVOT, self._config.MSA_BEST_USE_LONGEST_PIVOT, self._config.MSA_BEST_USE_CHARCONFS, \
                                               self._config.MSA_BEST_USE_WORDWISE_MSA, self._config.MSA_BEST_USE_SEARCHSPACE)
            else:
                #todo refactor this old stuff
                if self._config.MSA_BEST_USE_CHARCONFS is False:
                    if self._config.MSA_BEST_USE_N_DIST_PIVOT:
                        print("Doing: DO_MSA_BEST with MSA_BEST_USE_N_DIST_PIVOT")

                        ocr_comparison.do_msa_best_with_ndist_pivot()
                    else:
                        print("Doing: DO_MSA_BEST without NDIST_PIVOT")
                        ocr_comparison.do_msa_best()
                else:
                    if self._config.MSA_BEST_USE_N_DIST_PIVOT:
                        print("Doing: DO_MSA_BEST with MSA_BEST_USE_N_DIST_PIVOT and CHARCONFS")

                        ocr_comparison.do_msa_best_with_ndist_pivot_charconf()
                    else:
                        print("Doing: DO_MSA_BEST without NDIST_PIVOT and CHARCONFS")
                        print("This is not implemented yet")


            #ocr_comparison.print_msa_best_results()
            ocr_comparison.save_dataset_to_file(self._config.FILEPATH_MSA_BEST_RESULT, 0, self._config.MODE_ADD_LINEBREAKS, "msa_best")

        ocr_comparison.print_sets(False)


        if self._config.DO_ISRI_VAL is True:
            isri_handler = IsriHandler()

            # Test 'accuracy'
            isri_handler.accuracy(self._config.FILEPATH_GROUNDTRUTH, self._config.FILEPATH_NDIST_RESULT, self._config.FILEPATH_ACCURACY_REPORT_NDIST)
            isri_handler.accuracy(self._config.FILEPATH_GROUNDTRUTH, self._config.FILEPATH_MSA_BEST_RESULT, self._config.FILEPATH_ACCURACY_REPORT_MSA)

            # Test 'wordacc'
            isri_handler.wordacc(self._config.FILEPATH_GROUNDTRUTH, self._config.FILEPATH_NDIST_RESULT, None, self._config.FILEPATH_WACCURACY_REPORT_NDIST)
            isri_handler.wordacc(self._config.FILEPATH_GROUNDTRUTH, self._config.FILEPATH_MSA_BEST_RESULT, None, self._config.FILEPATH_WACCURACY_REPORT_MSA)

        if self._config.DISPLAY_DIFFERENCES:
            pyc_handler = PycharmHandler()
            pyc_handler.show_file_comparison(self._config.FILEPATH_GROUNDTRUTH, self._config.FILEPATH_NDIST_RESULT)
            pyc_handler.show_file_comparison(self._config.FILEPATH_GROUNDTRUTH, self._config.FILEPATH_MSA_BEST_RESULT)

            #testing strange wordaccuracy report production
            #pyc_handler.show_file_comparison(FILEPATH_NDIST_RESULT, FILEPATH_MSA_BEST_RESULT)
            #pyc_handler.show_file_comparison(FILEPATH_WACCURACY_REPORT_NDIST, FILEPATH_WACCURACY_REPORT_MSA)