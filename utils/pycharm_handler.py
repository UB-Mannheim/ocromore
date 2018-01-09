"""
Mind that this class requires pycharm installed and currently only is tested with Ubuntu Linux and pycharm.
In Pycharm create a command line launcher before using this class in Tools->Create Command-line Launcher...

Ideas for show_file_comparison:
Show multiple file-pairs in subsequent tabs


"""
from subprocess import call


class PycharmHandler(object):

    def __init__(self, os='Linux'):
        self.os = os

    def show_file_comparison(self, filepath_1, filepath_2):
        if self.os == 'Linux':
            try:
                call(["charm", "diff", filepath_1, filepath_2])
            except Exception as ex:
                print("Exception calling pycharm", ex)