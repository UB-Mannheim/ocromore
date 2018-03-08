from utils.df_objectifier import DFObjectifier
from n_dist_keying.ocr_comparison import OCRcomparison
from n_dist_keying.ocr_set import OCRset

class DatabaseHandler():

    def __init__(self, dataframe_wrapper, number_of_inputs):

        print("Init database handler")
        self._dataframe_wrapper = dataframe_wrapper
        self._number_of_inputs = number_of_inputs

    def get_some_empty_object(self):

        empty_object = self._dataframe_wrapper.get_obj(empty=True)
        return empty_object

    def create_ocr_set(self, input_list_db, line_index, fillup_empty_spaces=True):
        """
        Creates an ocr_set from given dataframe_wrapper
        #todo string comparison for ocr_setting and ocr_program costs much cpu, consider using enums or some keying
        :return:
        """
        USED_OCR_SETTING = 'default' # possible to add other settings later
        # indices in lineset for default setting
        DEFAULT_ABBY_INDEX = 0
        DEFAULT_TESS_INDEX = 1
        DEFAULT_OCROPUS_INDEX = 2


        ocr_set = OCRset(self._number_of_inputs, line_index)
        ocr_set.is_database_set(True, self)

        for input_element in input_list_db:

            ocr_program, ocr_setting = input_element.name

            if ocr_setting != USED_OCR_SETTING:
                continue

            if ocr_program == 'Abbyy':
                ocr_set.edit_line_set_value(DEFAULT_ABBY_INDEX, input_element)

            if ocr_program == 'Tess':
                ocr_set.edit_line_set_value(DEFAULT_TESS_INDEX, input_element)

            if ocr_program == 'Ocro':
                ocr_set.edit_line_set_value(DEFAULT_OCROPUS_INDEX, input_element)

        if fillup_empty_spaces is True:
            # fill up indices with no object
            for line_index in range(0, ocr_set.size):
                line = ocr_set.get_line_set_value_line(line_index)
                if line is False:
                    emptyobject = self.get_some_empty_object()
                    ocr_set.edit_line_set_value(line_index, emptyobject)

        #if len(ocr_set._set_lines) != len(input_list_db):
        #    print("asd")

        return  ocr_set

    def create_ocr_comparison(self):
        """
        Creates an ocr_comparison from dataframe,
        calls create_ocr_set multiple times
        :return: OCRComparison filled object
        """
        ocr_comparison = OCRcomparison()
        lines_object = self._dataframe_wrapper.get_line_obj()

        for line_index in lines_object:
            list_of_inputs = lines_object[line_index]
            ocr_set = self.create_ocr_set(list_of_inputs, line_index)
            ocr_comparison.add_set(ocr_set)


        return ocr_comparison