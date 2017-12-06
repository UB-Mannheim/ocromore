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


tesslistWOcro = get_ocropus_boxes("oneprof_tesseract.html")
tesslist = get_tesseract_boxes("oneprof_tesseract.html")