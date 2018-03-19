"""
Mind that this class requires isri-ocr-evaluation tools installed,
go to: https://github.com/eddieantonio/isri-ocr-evaluation-tools
download, build the tools and install globally

Tested for linux
Other systems will raise exception

"""
from subprocess import call
import os
from utils.conditional_print import ConditionalPrint
from configuration.configuration_handler import ConfigurationHandler


class IsriHandler(object):

    def __init__(self):
        self.os = os.name.lower()
        config_handler = ConfigurationHandler(first_init=False)
        self.config = config_handler.get_config()
        self.cpr = ConditionalPrint(self.config.PRINT_MSA_HANDLER, self.config.PRINT_EXCEPTION_LEVEL,
                                    self.config.PRINT_WARNING_LEVEL)
        if self.os != 'linux' or self.os != 'posix':
            raise OSError("Untested operating system adapt code and continue at own risk")


    def accuracy(self, path_correctfile, path_generatedfile, path_accuracy_report=""):
            try:
                call(["accuracy", path_correctfile, path_generatedfile, path_accuracy_report])
            except Exception as ex:
                self.cpr.printex("Exception calling pycharm", ex)


    class SynctextConfig(object):

        def __init__(self):
            self._used_config_acc =[]

        def use_T_algorithm(self):
            self._used_config_acc.append("-T")

        def use_H_algorithm(self):
            self._used_config_acc.append("-H")

        def use_case_insensitive(self):
            self._used_config_acc.append("-i")

        def use_display_suspect_markers_in_output(self):
            self._used_config_acc.append("-s")

        def get_used_config(self):
            return self._used_config_acc

        def clear_used_config(self):
            self._used_config_acc = []


    def synctext(self, filepaths, path_generatedfile=None, synctext_config = SynctextConfig()):

        try:
            flags = synctext_config.get_used_config()
            calls = ["synctext"]
            calls.extend(flags)
            calls.extend(filepaths)

            if path_generatedfile is None:
                call(calls)
            else:
                filehandle = self.create_file_if_doesnt_exist(path_generatedfile, True)
                call(calls, stdout=filehandle)
                filehandle.close()

        except Exception as ex:
            self.cpr.printex("Exception calling pycharm", ex)

    def accsum(self, filepaths_accreports, path_generatedfile=None):

        try:
            calls = ["accsum"]
            calls.extend(filepaths_accreports)

            if path_generatedfile is None:
                call(calls)
            else:
                filehandle = self.create_file_if_doesnt_exist(path_generatedfile, True)
                call(calls, stdout=filehandle)
                filehandle.close()

        except Exception as ex:
            self.cpr.printex("Exception calling pycharm", ex)


    def groupacc(self, path_groupfile, path_accuracy_report, path_groupacc_report = None):

        try:
            calls = ["groupacc"]
            calls.append(path_groupfile)
            calls.append(path_accuracy_report)

            if path_groupacc_report is None:
                call(calls)
            else:
                filehandle = self.create_file_if_doesnt_exist(path_groupacc_report, True)
                filehandle.close()
                calls.append(path_groupacc_report)
                call(calls)

        except Exception as ex:
            self.cpr.printex("Exception calling pycharm", ex)

    def accdist(self, filepaths_accreports, path_generated_xyfile=None):

        try:
            calls = ["accdist"]
            calls.extend(filepaths_accreports)

            if path_generated_xyfile is None:
                call(calls)
            else:
                filehandle = self.create_file_if_doesnt_exist(path_generated_xyfile, True)
                call(calls, stdout=filehandle)
                filehandle.close()

        except Exception as ex:
            self.cpr.printex("Exception calling pycharm", ex)

    class NGramConfig(object):

        def __init__(self):
            self._used_config_acc =[]

        def set_ngram_size(self, number):
            if number>=1 and number <= 3:
                self._used_config_acc.append("-n")
                self._used_config_acc.append(str(number))

        def clear_used_config(self):
            self._used_config_acc = []

        def get_used_config(self):
            return self._used_config_acc

    def ngram(self, filepaths, path_generatedfile = None, ngram_config = NGramConfig()):

        try:
            flags = ngram_config.get_used_config()
            calls = ["ngram"]
            calls.extend(flags)
            calls.extend(filepaths)

            if path_generatedfile is None:
                call(calls)
            else:
                filehandle = self.create_file_if_doesnt_exist(path_generatedfile, True)
                call(calls, stdout=filehandle)
                filehandle.close()

        except Exception as ex:
            self.cpr.printex("Exception calling pycharm", ex)

    class VoteConfig(object):

        def __init__(self):
            self._used_config_acc =[]

        def enable_O_optimization(self):
            self._used_config_acc.append("-O")

        def set_s(self, fraction_counter, fraction_denominator):
            self._used_config_acc.append("-s")
            self._used_config_acc.append(fraction_counter+"/"+fraction_denominator)

        def set_w(self, fraction_counter, fraction_denominator):
            self._used_config_acc.append("-w")
            self._used_config_acc.append(fraction_counter+"/"+fraction_denominator)


        def set_output_file(self, path_outputfile):
            self._used_config_acc.append("-o")
            self._used_config_acc.append(path_outputfile) #ok?

        def clear_used_config(self):
            self._used_config_acc = []

        def get_used_config(self):
            return self._used_config_acc

    def vote(self, filepaths, ngram_config = VoteConfig()):

        try:

            flags = ngram_config.get_used_config()
            calls = ["vote"]
            calls.extend(flags)
            calls.extend(filepaths)

            call(calls)

        except Exception as ex:
            self.cpr.printex("Exception calling pycharm", ex)



    def wordacc(self, path_correctfile, path_comparison_file, path_stopwordfile = None, path_wordacc_report = None):

        try:
            calls = ["wordacc"]

            if path_stopwordfile is not None:
                calls.append("-S")
                calls.append(path_stopwordfile)

            calls.append(path_correctfile)
            calls.append(path_comparison_file)

            if path_wordacc_report is not None:
                calls.append(path_wordacc_report)

            call(calls)

        except Exception as ex:
            self.cpr.printex("Exception calling pycharm", ex)


    def wordaccsum(self, filepaths_wordacc_reports, path_accsumreport=None):

        try:
            calls = ["wordaccsum"]
            calls.extend(filepaths_wordacc_reports)

            if path_accsumreport is None:
                call(calls)
            else:
                filehandle = self.create_file_if_doesnt_exist(path_accsumreport, True)
                call(calls, stdout=filehandle)
                filehandle.close()

        except Exception as ex:
            self.cpr.printex("Exception calling pycharm", ex)

    def nonstopacc(self, path_stopwordfile, path_wordacc_report,  path_output_xyfile=None):

        try:
            calls = ["nonstopacc"]
            calls.append(path_stopwordfile)
            calls.append(path_wordacc_report)



            if path_output_xyfile is None:
                call(calls)
            else:
                filehandle = self.create_file_if_doesnt_exist(path_output_xyfile, True)
                call(calls, stdout=filehandle)
                filehandle.close()

        except Exception as ex:
            self.cpr.printex("Exception calling pycharm", ex)



    def wordaccci(self, filepaths_wordacc_reports,  path_outputfile=None):

        try:
            calls = ["wordaccci"]
            calls.extend(filepaths_wordacc_reports)

            if path_outputfile is None:
                call(calls)
            else:
                filehandle = self.create_file_if_doesnt_exist(path_outputfile, True)
                call(calls, stdout=filehandle)
                filehandle.close()

        except Exception as ex:
            self.cpr.printex("Exception calling pycharm", ex)

    def wordaccdist(self, filepaths_wordacc_reports,  path_output_xyfile=None):

        try:
            calls = ["wordaccdist"]
            calls.extend(filepaths_wordacc_reports)

            if path_output_xyfile is None:
                call(calls)
            else:
                filehandle = self.create_file_if_doesnt_exist(path_output_xyfile, True)
                call(calls, stdout=filehandle)
                filehandle.close()

        except Exception as ex:
            self.cpr.printex("Exception calling pycharm", ex)

    def wordfreq(self, filepaths_inputtext,  path_resultfile=None):

        try:
            calls = ["wordfreq"]
            calls.extend(filepaths_inputtext)

            if path_resultfile is None:
                call(calls)
            else:
                filehandle = self.create_file_if_doesnt_exist(path_resultfile, True)
                call(calls, stdout=filehandle)
                filehandle.close()

        except Exception as ex:
            self.cpr.printex("Exception calling pycharm", ex)

    #todo add the zoning programs some day: point 4 in doc
    def editop(self, path_correctfile, path_comparison_file, path_editop_report = None):

        try:
            calls = ["editop"]


            calls.append(path_correctfile)
            calls.append(path_comparison_file)

            if path_editop_report is not None:
                calls.append(path_editop_report)

            call(calls)

        except Exception as ex:
            self.cpr.printex("Exception calling pycharm", ex)

    def editopsum(self, filepaths_editopreports,  path_summed_report=None):

        try:
            calls = ["editopsum"]
            calls.extend(filepaths_editopreports)

            if path_summed_report is None:
                call(calls)
            else:
                filehandle = self.create_file_if_doesnt_exist(path_summed_report, True)
                call(calls, stdout=filehandle)
                filehandle.close()

        except Exception as ex:
            self.cpr.printex("Exception calling pycharm", ex)

    def editopcost(self, path_editop_report, path_editop_report2=None, path_output_xyfile=None):

        try:
            calls = ["editopcost"]


            calls.append(path_editop_report)


            if path_editop_report2 is not None:
                calls.append(path_editop_report2)

            if path_output_xyfile is None:
                call(calls)
            else:
                filehandle = self.create_file_if_doesnt_exist(path_output_xyfile, True)
                call(calls, stdout=filehandle)
                filehandle.close()

        except Exception as ex:
            self.cpr.printex("Exception calling pycharm", ex)

    def create_file_if_doesnt_exist(self, filepath, overwrite = False):

        file = open(filepath, 'w+')
        if overwrite:
            self.delete_file_content(file)
        return file

    def delete_file_content(self, pfile):
        pfile.seek(0)
        pfile.truncate()