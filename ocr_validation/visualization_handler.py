"""
Mind that this class requires pycharm installed and currently only is tested with Ubuntu Linux and pycharm.
In Pycharm create a command line launcher before using this class in Tools->Create Command-line Launcher...



Also requires meld


"""
from subprocess import Popen
import os
from utils.conditional_print import ConditionalPrint
from configuration.configuration_handler import ConfigurationHandler


class VisualizationHandler(object):

    def __init__(self):
        self.os = os.name.lower()
        config_handler = ConfigurationHandler(first_init=False)
        self.config = config_handler.get_config()
        self.cpr = ConditionalPrint(self.config.PRINT_MSA_HANDLER, self.config.PRINT_EXCEPTION_LEVEL,
                                    self.config.PRINT_WARNING_LEVEL)

    def show_file_comparison_pycharm(self, filepath_1, filepath_2):
        if self.os == 'linux' or self.os == 'posix':
            try:
                process = Popen(["charm", "diff", filepath_1, filepath_2])
                return process

            except Exception as ex:
                self.cpr.printex("Exception calling pycharm", ex)
        else:
            self.cpr.printex("Write code here for other os, or take other os")

        return None


    def show_file_comparison_meld(self, filepath_1, filepath_2, just_add_tab = False):
        if self.os == 'linux' or self.os == 'posix':
            try:
                if just_add_tab:
                    process = Popen(["meld", "--newtab", filepath_1, filepath_2])
                else:
                    process = Popen(["meld", filepath_1, filepath_2])
                return process

            except Exception as ex:
                self.cpr.printex("Exception calling meld", ex)
        else:
            self.cpr.printex("Write code here for other os, or take other os")

        return None
