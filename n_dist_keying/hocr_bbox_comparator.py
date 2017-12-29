import os
from my_hocr_parser.parser import HOCRDocument, Line, Paragraph, Area
from n_dist_keying.text_comparator import TextComparator
from n_dist_keying.ocr_comparison import OCRcomparison
from n_dist_keying.ocr_set import OCRset
from n_dist_keying.marker import Marker

class HocrBBoxComparator(object):

    def get_hocr_document(self, filename):

        dir_path = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(dir_path, filename)
        document = HOCRDocument(full_path, is_path=True)
        return document

    def get_ocropus_boxes(self, filename):
        """
        Gets the box information for ocropus
        :param filename: name of the file to check for boxes
        :return: list of lines with boxes
        """

        document = self.get_hocr_document(filename)
        page = document.pages[0]

        html = page._hocr_html
        contents = html.contents
        return_list = []
        for element in contents:
            res = str(element).find("span")
            if res >= 1:
                liner = Line(document, element)
                return_list.append(liner)

        return return_list

    def get_tesseract_boxes(self, filename):

        document = self.get_hocr_document(filename)
        page = document.pages[0]
        return_list = []

        for c_area in page.areas:
            for c_paragraph in c_area.paragraphs:
                for c_line in c_paragraph.lines:
                    return_list.append(c_line)
                    # for c_word in c_line.words:
                    # print(c_word.ocr_text)

        return return_list

    def get_abbyy_boxes(self, filename):

        document = self.get_hocr_document(filename)
        page = document.pages[0]

        html = page._hocr_html
        contents = html.contents
        return_list = []
        for element in contents:
            res = str(element).find("ocr_line")
            if res >= 1:
                # in abbyy-hocr sometimes the lines are packed in ocr_careas and sometimes not
                # this reads all the lines in correct order
                if element.attrs['class'][0] == 'ocr_carea':
                    new_area = Area(None, element)
                    for par in new_area.paragraphs:
                        for line in par.lines:
                            return_list.append(line)

                elif element.attrs['class'][0] == 'ocr_par':
                    par = Paragraph(None, element)
                    for line in par.lines:
                        return_list.append(line)

                else:
                    raise Exception('THIS SHOULDNT HAPPEN!')

        return return_list

    def compare_coordinates(self, coordinates1, coordinates2):
        MODE = "ENDPOINT_TRESHOLD"

        (x1_start, y1_start, x1_end, y1_end) = coordinates1
        (x2_start, y2_start, x2_end, y2_end) = coordinates2

        if MODE == "ENDPOINT_TRESHOLD":
            TRESHOLD_VALUE = 30
            y_start_diff = abs(y1_start - y2_start)
            y_end_diff = abs(y1_end - y2_end)
            if (y_start_diff < TRESHOLD_VALUE and y_end_diff < TRESHOLD_VALUE):
                return True
            else:
                return False
        if MODE == "OVERLAPPING_SIZE":
            TRESHOLD_VALUE = 12
            # todo implement this alternative mode, if necessary



    def compare_lists_old(self, ocro_list, tess_list, abbyy_list):
        """
        Prints a basic comparison of lists for TESTING

        :param ocro_list:
        :param tess_list:
        :param abbyy_list:
        :return:
        """
        Y_TRESH = 10
        TESSERACT_COMPARE = False
        ABBY_COMPARE = True

        for ocro_line in ocro_list:
            # search correspondence
            ocro_coordinates = ocro_line.coordinates
            if TESSERACT_COMPARE:
                for tess_line in tess_list:
                    tess_coordinates = tess_line.coordinates
                    cmpr_result = self.compare_coordinates(ocro_coordinates, tess_coordinates)
                    if cmpr_result:
                        """Extract and subtract text from boxes"""
                        tess_line_text = tess_line.ocr_text
                        print("Tesseract Box:         ", tess_line_text)
                        ocro_line_text = ocro_line._hocr_html.contents[0]
                        print("Ocropus Box  :         ", ocro_line_text)
                        result1 = TextComparator.compare_ocr_strings_cwise(tess_line_text, ocro_line_text)
                        print("tesseract-ocropus:     ", result1)
                        result2 = TextComparator.compare_ocr_strings_cwise(ocro_line_text, tess_line_text)
                        print("ocropus-tesseract:     ", result2)
                        result3 = TextComparator.compare_ocr_strings_cwise(tess_line_text, ocro_line_text, True)
                        print("tesseract-ocropus (ic):", result3)
                        result4 = TextComparator.compare_ocr_strings_cwise(ocro_line_text, tess_line_text, True)
                        print("ocropus-tesseract (ic):", result4)
                        print("--------")
                        break
            if ABBY_COMPARE:
                for abby_line in abbyy_list:
                    abbyy_coordinates = abby_line.coordinates
                    cmpr_result = self.compare_coordinates(ocro_coordinates, abbyy_coordinates)
                    if cmpr_result:
                        """Extract and subtract text from boxes"""
                        abbyy_line_text = abby_line.ocr_text
                        print("Abbyy Box:         ", abbyy_line_text)
                        ocro_line_text = ocro_line._hocr_html.contents[0]
                        print("Ocropus Box  :         ", ocro_line_text)
                        result1 = TextComparator.compare_ocr_strings_cwise(abbyy_line_text, ocro_line_text)
                        print("abbyy-ocropus:     ", result1)
                        result2 = TextComparator.compare_ocr_strings_cwise(ocro_line_text, abbyy_line_text)
                        print("ocropus-abby:     ", result2)
                        result3 = TextComparator.compare_ocr_strings_cwise(abbyy_line_text, ocro_line_text, True)
                        print("abbyy-ocropus (ic):", result3)
                        result4 = TextComparator.compare_ocr_strings_cwise(ocro_line_text, abbyy_line_text, True)
                        print("ocropus-abbyy (ic):", result4)

                        # this just logs blocks

                        # compare_ocr_strings_difflib_seqmatch(ocro_line_text, tess_line_text)

                        # result5 = compare_ocr_strings_difflib_difftool(ocro_line_text, abbyy_line_text)

                        print("--------")
                        break

    def get_matches_in_other_lists(self, my_list_index, my_ocr_lists, line_element):

        my_current_set = OCRset(len(my_ocr_lists), None)
        my_current_set.edit_line_set_value(my_list_index, line_element)

        # this is the search loop which finds matches in each list
        for list_index, ocr_list in enumerate(my_ocr_lists):
            if list_index is my_list_index:
                # don't compare the same list
                continue

            for line_element_compare in ocr_list:
                if Marker.is_not_marked(line_element_compare):
                    cmpr_result = self.compare_coordinates(line_element.coordinates, line_element_compare.coordinates)
                    if cmpr_result is True:
                        Marker.mark_element(line_element_compare)
                        my_current_set.edit_line_set_value(list_index, line_element_compare)
                        if my_current_set.is_full():
                            break

        Marker.mark_element(line_element)
        my_current_set.calculate_y_mean()
        return my_current_set

    def compare_lists(self, ocr_lists):

        return_comparison = OCRcomparison()

        # this is the big loop which goes trough every element
        for list_index, ocr_list in enumerate(ocr_lists):
            for line_element in ocr_list:
                if Marker.is_not_marked(line_element):
                    set_created = self.get_matches_in_other_lists(list_index, ocr_lists, line_element)
                    return_comparison.add_set(set_created)

        return return_comparison