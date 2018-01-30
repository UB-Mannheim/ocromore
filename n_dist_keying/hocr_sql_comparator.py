import os
from my_hocr_parser.parser import HOCRDocument, Line, Paragraph, Area
from n_dist_keying.text_comparator import TextComparator
from n_dist_keying.ocr_comparison import OCRcomparison
from n_dist_keying.ocr_set import OCRset
from n_dist_keying.marker import Marker
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
import matplotlib.pyplot as plt
import sys
from sqlalchemy import create_engine
import zlib


class HocrSQLComparator(object):

    def __init__(self):
        self._ocropus_page = None
        self._abbyy_page = None
        self._tesseract_page = None


    def get_hocr_document(self, filename):

        dir_path = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(dir_path, filename)
        document = HOCRDocument(full_path, is_path=True)
        return document

    def create_table_ocropus(self, filename, ocr_profile=None):
        """
        Gets the box information for ocropus
        :param filename: name of the file to check for boxes
        :return: list of lines with boxes
        """

        document = self.get_hocr_document(filename)
        page = document.pages[0]

        # assign ocropus page
        self._ocropus_page = page

        html = page._hocr_html
        contents = html.contents
        lidx = 0
        dfdict = {}
        idx = 0
        ocr = "Ocropus"
        if not ocr_profile:
            ocr_profile = "default"
        for element in contents:
            res = str(element).find("span")
            if res >= 1:
                line = Line(document, element)
                for widx, word in enumerate(line.words):
                    for cidx, char in enumerate(word.ocr_text):
                        if len(word._xconfs) > cidx:
                            dfdict[idx] = {
                                "ocr"           : ocr,
                                "ocr_profile"   : ocr_profile,
                                "line_idx"      : lidx,
                                "word_idx"      : widx,
                                "char_idx"      : cidx,
                                "char"          : char,
                                "char_eval"     : "",
                                "char_weight"   : -1.0,
                                "x_confs"       : float(word._xconfs[cidx])+4,
                                "w_confs"       : float(word._xwconf),
                                "line_match"    : -1,
                                "line_x0"       : int(line.coordinates[0]),
                                "line_x1"       : int(line.coordinates[1]),
                                "line_y0"       : int(line.coordinates[2]),
                                "line_y1"       : int(line.coordinates[3]),
                                "word_x0"       : int(word.coordinates[0]),
                                "word_x1"       : int(word.coordinates[1]),
                                "word_y0"       : int(word.coordinates[2]),
                                "word_y1"       : int(word.coordinates[3]),
                            }
                            idx += 1
                lidx+=1

        # creating and indexing the dataframe
        df_new = pd.DataFrame.from_dict(dfdict,orient='index')
        df_new = df_new.set_index(['ocr','line_idx','word_idx','char_idx'])


        # creating and appending database
        engine = create_engine('sqlite:////media/sf_ShareVB/test.db', echo=True)
        tablename = str(os.path.basename(filename)).split(".")[0]

        # try to create a table
        try:
            df_new.to_sql(tablename,engine)
            print(f'The table:"{tablename}" was created!')
        except:
            # loading the table
            df_old = pd.read_sql_table(tablename,engine)
            df_old = df_old.set_index(['ocr','line_idx','word_idx','char_idx'])
            df_old.update(df_new)
            df_old.to_sql(tablename,engine,if_exists='replace')
            print(f'The table:"{tablename}" was updated!')
        return 0

    def create_table_tesseract(self, filename, ocr_profile=None):

        document = self.get_hocr_document(filename)
        page = document.pages[0]

        # assign tesseract page for further usage
        self._tesseract_page = page

        dfdict = {}
        idx = 0
        lidx = 0
        ocr = "Tesseract"
        if not ocr_profile:
            ocr_profile = "default"
        for area in page.areas:
            for paragraph in area.paragraphs:
                for line in paragraph.lines:
                    for widx, word in enumerate(line.words):
                        for cidx, char in enumerate(word.ocr_text):
                            if len(word._xconfs) > cidx:
                                dfdict[idx] = {
                                    "ocr"           : ocr,
                                    "ocr_profile"   : ocr_profile,
                                    "line_idx"      : lidx,
                                    "word_idx"      : widx,
                                    "char_idx"      : cidx,
                                    "char"          : char,
                                    "char_eval"     : "",
                                    "char_weight"   : -1.0,
                                    "x_confs"       : word._xconfs[cidx],
                                    "w_confs"       : word._xwconf,
                                    "line_match"    : -1,
                                    "line_x0"       : line.coordinates[0],
                                    "line_x1"       : line.coordinates[1],
                                    "line_y0"       : line.coordinates[2],
                                    "line_y1"       : line.coordinates[3],
                                    "word_x0"       : word.coordinates[0],
                                    "word_x1"       : word.coordinates[1],
                                    "word_y0"       : word.coordinates[2],
                                    "word_y1"       : word.coordinates[3],
                                    "uid"           : ' '.join([ocr,ocr_profile,str(lidx),str(widx),str(cidx)]),
                                }
                                idx += 1
                    lidx += 1
        df = pd.DataFrame.from_dict(dfdict, orient='index')
        # obsolete?
        # df = df.set_index(['ocr','line_idx','word_idx','char_idx'])

        df = df.set_index(['ocr','line_idx','word_idx','char_idx'])
        engine = create_engine('sqlite:////home/jkamlah/Coding/akf-sql/test.db', echo=True)
        df.to_sql(str(os.path.basename(filename)).split(".")[0], engine, if_exists='append')
        return dfdict

    def create_table_abby(self, filename):

        document = self.get_hocr_document(filename)
        page = document.pages[0]

        # assign abbyy page for further usage
        self._abbyy_page = page

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