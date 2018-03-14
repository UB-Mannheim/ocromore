from utils.df_objectifier import DFObjectifier
from n_dist_keying.database_handler import DatabaseHandler
from utils.pycharm_handler import PycharmHandler
from ocr_validation.isri_handler import IsriHandler
from os import listdir
from os.path import isfile, join
import os
import shutil



class TableParser(object):


    def __init__(self, config):

        print("asd")
        self._config = config
        # give the last element in split path
        self._base_db_dir = os.path.basename(os.path.normpath(config.DBDIR))

    def delete_output_dir(self):
        # delete database directory
        if os.path.exists(self._config.OUTPUT_ROOT_PATH):
            shutil.rmtree(self._config.OUTPUT_ROOT_PATH)

    def create_output_dir(self):

        # dcreate database directory
        os.makedirs(self._config.OUTPUT_ROOT_PATH)

    def create_isri_reports(self, filestructs, addendum):

        acc_reports = []
        wacc_reports = []
        db_root_path = ""
        for db in filestructs:
            files = filestructs[db]
            file = files[0]
            # assume that each db has different root folder, just take first file for path reference
            dbpath = 'sqlite:////' + file.dbpath
            dbname = file.dbname
            db_root_path = self.get_basic_output_directory(dbpath, addendum)
            if os.path.exists(db_root_path):
                fp_gen_acc_report, fp_gen_wacc_report = \
                    self.summarize_accuracy_reports(db_root_path, dbname)
                acc_reports.append(fp_gen_acc_report)
                wacc_reports.append(fp_gen_wacc_report)

        # create big accumulated report
        output_root_path = os.path.dirname(db_root_path)
        self.summarize_accuracy_report_sums(wacc_reports, acc_reports, output_root_path)



    def get_basic_output_directory(self, dbdir_abs, addendum):
        basename_db_ext = os.path.basename(os.path.normpath(dbdir_abs))
        basename_db = os.path.splitext(basename_db_ext)[0] # remove extension
        basic_output_dir = self._config.OUTPUT_ROOT_PATH + "/" + self._base_db_dir+"_"+addendum + "/" + basename_db
        return basic_output_dir

    def parse_a_table(self, dbdir_abs, table):

        # basename_db_ext = os.path.basename(os.path.normpath(dbdir_abs))
        # basename_db = os.path.splitext(basename_db_ext)[0] # remove extension
        additional_created_files = []

        dataframe_wrapper = DFObjectifier(dbdir_abs, table)
        database_handler = DatabaseHandler(dataframe_wrapper, self._config.NUMBER_OF_INPUTS)
        ocr_comparison = database_handler.create_ocr_comparison()
        ocr_comparison.sort_set()
        print("Print mean||decision||abbyy||tesseract||ocropus|||| without unspacing-------------------")
        ocr_comparison.print_sets(False)

        if self._config.SAVE_INPUT_DATASETS_TO_FILE:

            output_path_abbyy = self.get_basic_output_directory(dbdir_abs, "abbyy") + "/" + table + "_abbyy.txt"
            output_path_tess = self.get_basic_output_directory(dbdir_abs, "tess") + "/" + table + "_tess.txt"
            output_path_ocro = self.get_basic_output_directory(dbdir_abs, "ocro") + "/" + table + "_ocro.txt"


            ocr_comparison.save_dataset_to_file(output_path_abbyy, 0, mode_add_linebreaks=False)
            ocr_comparison.save_dataset_to_file(output_path_tess, 1, mode_add_linebreaks=False)
            ocr_comparison.save_dataset_to_file(output_path_ocro, 2, mode_add_linebreaks=False)

            additional_created_files.append(output_path_abbyy)
            additional_created_files.append(output_path_tess)
            additional_created_files.append(output_path_ocro)



            print("asd")
            # ocr_comparison.save_dataset_to_file()

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

            # created_path = self._config.OUTPUT_ROOT_PATH+"/"+self._base_db_dir+"//"+basename_db+"//"+table+"_msa_best.txt"

            created_path = self.get_basic_output_directory(dbdir_abs,"msa_best") + "/" + table + "_msa_best.txt"

            ocr_comparison.save_dataset_to_file(created_path, 0, self._config.MODE_ADD_LINEBREAKS, "msa_best")
            return created_path, additional_created_files

    def validate_table_against_gt(self, filepath_table, filepath_groundtruth):
        if self._config.DO_ISRI_VAL is True:
            isri_handler = IsriHandler()

            # Test 'accuracy'
            isri_handler.accuracy(filepath_groundtruth, filepath_table, filepath_table+".accreport")

            # Test 'wordacc'
            isri_handler.wordacc(filepath_groundtruth, filepath_table, None, filepath_table+".waccreport")

    def summarize_accuracy_report_sums(self, waccreports, accreports, output_root_path):
        if self._config.SUMMARIZE_ISRI_REPORTS is False:
            return None, None

        basename = os.path.basename(output_root_path)
        isri_handler = IsriHandler()
        isri_handler.accsum(accreports, output_root_path+"/"+basename+"_complete_summarized_report.accsum")
        isri_handler.wordaccsum(waccreports, output_root_path+"/"+basename+"_complete_summarized_report.waccsum")



    def summarize_accuracy_reports(self, root_folder, dbname):
        if self._config.SUMMARIZE_ISRI_REPORTS is False:
            return None, None

        isri_handler = IsriHandler()
        # isri_handler.accsum()
        # isri_handler.wordaccsum()
        # isri_handler.groupacc()

        onlyfiles = [f for f in listdir(root_folder) if isfile(join(root_folder, f))]

        files_waccsum = []
        files_accsum = []
        for file in onlyfiles:
            if file.endswith(".waccreport"):
                files_waccsum.append(root_folder+"/"+file)
            elif file.endswith(".accreport"):
                files_accsum.append(root_folder+"/"+file)

        generated_acc_report = root_folder+"/"+dbname+"_summarized_report.accsum"
        generated_wacc_report = root_folder+"/"+dbname+"_summarized_report.waccsum"
        isri_handler.accsum(files_accsum, generated_acc_report )
        isri_handler.wordaccsum(files_waccsum, generated_wacc_report)


        return generated_acc_report, generated_wacc_report

    def display_stuff(self):
        # not used atm
        if self._config.DISPLAY_DIFFERENCES:
            pyc_handler = PycharmHandler()
            pyc_handler.show_file_comparison(self._config.FILEPATH_GROUNDTRUTH, self._config.FILEPATH_NDIST_RESULT)
            pyc_handler.show_file_comparison(self._config.FILEPATH_GROUNDTRUTH, self._config.FILEPATH_MSA_BEST_RESULT)

            #testing strange wordaccuracy report production
            #pyc_handler.show_file_comparison(FILEPATH_NDIST_RESULT, FILEPATH_MSA_BEST_RESULT)
            #pyc_handler.show_file_comparison(FILEPATH_WACCURACY_REPORT_NDIST, FILEPATH_WACCURACY_REPORT_MSA)