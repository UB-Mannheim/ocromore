"""
    https://github.com/athento/hocr-parser

"""

import os
from hocr_parser.parser import HOCRDocument,Line,Paragraph
from bs4 import Tag
from bs4 import BeautifulSoup

def get_ocropus_boxes(filename):
    """
    Gets the box information for ocropus
    :param filename: name of the file to check for boxes
    :return: list of lines with boxes
    """
    dir_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(dir_path, filename)
    document = HOCRDocument(full_path, is_path=True)
    page = document.pages[0]

    html = page._hocr_html
    contents = html.contents
    return_list = []
    for element in contents:
        res = str(element).find("span")
        if res>=1:
            liner = Line(document,element)
            return_list.append(liner)

    return return_list


ocrolist = get_ocropus_boxes("oneprof_ocropus.html")


def get_tesseract_boxes(filename):
    dir_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(dir_path, filename)
    document = HOCRDocument(full_path, is_path=True)
    page = document.pages[0]
    return_list = []

    for c_area in page.areas:
        for c_paragraph in c_area.paragraphs:
            for c_line in c_paragraph.lines:
                return_list.append(c_line)
                # for c_word in c_line.words:
                    # print(c_word.ocr_text)

    return return_list


tesslist = get_tesseract_boxes("oneprof_tesseract.html")


def compare_coordinates(coordinates1, coordinates2):
    MODE = "ENDPOINT_TRESHOLD"

    (x1_start, y1_start, x1_end, y1_end) = coordinates1
    (x2_start, y2_start, x2_end, y2_end) = coordinates2

    if MODE == "ENDPOINT_TRESHOLD":
        TRESHOLD_VALUE = 10
        y_start_diff = abs(y1_start - y2_start)
        y_end_diff = abs(y1_end - y2_end)
        if (y_start_diff < TRESHOLD_VALUE and y_end_diff < TRESHOLD_VALUE):
            return True
        else:
            return False
    if MODE == "OVERLAPPING_SIZE":
        TRESHOLD_VALUE = 12


def compare_ocr_strings_cwise(ocr_string1,ocr_string2, ignore_case = False):
    """
    Character-wise comparison of ocr strings
    :param ocr_string1: input string 1
    :param ocr_string2: input string 2
    :param ignore_case: if True, no case sensivity, cast everything (including result) to lowercase
    :return: ocr_string1 subtracted by the characters in ocr_string2
    """

    # simple method for ignore case, just downcast everything to lowercase
    if ignore_case:
        ocr_string1 = ocr_string1.lower()
        ocr_string2 = ocr_string2.lower()

    final_string = ocr_string1
    for char in ocr_string2:
        if final_string.find(char) >= 0:
            final_string = final_string.replace(char, '')

    return final_string


def compare_lists(ocro_list,tess_list):

    Y_TRESH=10

    for ocro_line in ocro_list:
        #search correspondence
        ocro_coordinates = ocro_line.coordinates
        for tess_line in tess_list:
            tess_coordinates = tess_line.coordinates
            cmpr_result = compare_coordinates(ocro_coordinates,tess_coordinates)
            if cmpr_result:
                """Extract and subtract text from boxes"""
                tess_line_text = tess_line.ocr_text
                print("Tesseract Box: \t", tess_line_text)
                ocro_line_text = ocro_line._hocr_html.contents[0]
                print("Ocropus Box  : \t", ocro_line_text)

                result1 = compare_ocr_strings_cwise(tess_line_text, ocro_line_text)
                print("tesseract-ocropus: \t", result1)
                result2 = compare_ocr_strings_cwise(ocro_line_text,tess_line_text)
                print("ocropus-tesseract: \t", result2)
                result3 = compare_ocr_strings_cwise(tess_line_text, ocro_line_text, True)
                print("tesseract-ocropus (ic): \t", result3)
                result4 = compare_ocr_strings_cwise(ocro_line_text, tess_line_text, True)
                print("ocropus-tesseract (ic): \t", result4)
                print("--------")
                break





compare_lists(ocrolist,tesslist)