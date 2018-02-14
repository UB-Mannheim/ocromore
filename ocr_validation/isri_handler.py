"""
Mind that this class requires isri-ocr-evaluation tools installed,
go to: https://github.com/eddieantonio/isri-ocr-evaluation-tools
download, build the tools and install globally

Tested for linux
Other systems will raise exception

"""
from subprocess import call


class IsriHandler(object):

    def __init__(self, os='Linux'):
        self.os = os

        if self.os != 'Linux':
            raise OSError("Untested operating system adapt code and continue at own risk")


    def accuracy(self, path_correctfile, path_generatedfile, path_accuracy_report=""):
            try:
                call(["accuracy", path_correctfile, path_generatedfile, path_accuracy_report])
            except Exception as ex:
                print("Exception calling pycharm", ex)


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

        # just for testing can be used for more files!
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
            print("Exception calling pycharm", ex)


    def create_file_if_doesnt_exist(self, filepath, overwrite = False):

        file = open(filepath, 'w+')
        if overwrite:
            self.delete_file_content(file)
        return file

    def delete_file_content(self, pfile):
        pfile.seek(0)
        pfile.truncate()