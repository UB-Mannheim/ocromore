__author__ = 'Rafa Haro <rh@athento.com>'

from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup
import re


class HOCRElement:

    __metaclass__ = ABCMeta

    COORDINATES_PATTERN = re.compile("bbox\s(-?[0-9]+)\s(-?[0-9]+)\s(-?[0-9]+)\s(-?[0-9]+)")

    def __init__(self, hocr_html, parent, next_tag, next_attribute, next_class):
        self.__coordinates = (0, 0, 0, 0)
        self._hocr_html = hocr_html
        self._id = None
        self._parent = parent
        self._elements = self._parse(next_tag, next_attribute, next_class)

    def _parse(self, next_tag, next_attributte, next_class):

        try:
            self._id = self._hocr_html['id']
        except KeyError:
            self._id = None

        try:
            title = self._hocr_html['title']
            match = HOCRElement.COORDINATES_PATTERN.search(title)
            if match:
                self.__coordinates = (int(match.group(1)),
                                      int(match.group(2)),
                                      int(match.group(3)),
                                      int(match.group(4)))
            else:
                raise ValueError("The HOCR element doesn't contain a valid title property")
        except KeyError:
            self.__coordinates = (0, 0, 0, 0)

        elements = []
        if next_tag is not None and next_class is not None:
            for html_element in self._hocr_html.find_all(next_tag, {'class':next_attributte}):
                elements.append(next_class(self, html_element))
        return elements

    @property
    def coordinates(self):
        return self.__coordinates

    @property
    def html(self):
        return self._hocr_html.prettify()

    @property
    def id(self):
        return self._id

    @property
    def parent(self):
        return self._parent

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        if not isinstance(other, HOCRElement):
            return False
        else:
            return self._id == other._id

    @property
    @abstractmethod
    def ocr_text(self):
        pass

class HOCRDocument(HOCRElement):

    def __init__(self, source, is_path=False):

        if not is_path:
            hocr_html = BeautifulSoup(source, 'html.parser')
        else:
            hocr_html = BeautifulSoup(open(source, 'r', encoding="utf-8").read(), 'html.parser')

        super(HOCRDocument, self).__init__(hocr_html, None, 'div', Page.HOCR_PAGE_TAG, Page)

    @property
    def ocr_text(self):
        output = ""
        for element in self._elements[:-1]:
            output += element.ocr_text
            output += "\n\n"
        output += self._elements[-1].ocr_text
        return output

    @property
    def pages(self):
        return self._elements

    @property
    def npages(self):
        return len(self._elements)

    @property
    def ocr(self):
        for tag in self._hocr_html.find_all("meta"):
            if "esseract" in tag.get("content",None):
                return "Tess"
            if "cropy" in tag.get("content",None):
                return "Ocro"
            if "ABBYY" in tag.get("content",None):
                return "Abbyy"
        return "Abbyy"

class Page(HOCRElement):

    HOCR_PAGE_TAG = "ocr_page"

    def __init__(self, parent, hocr_html):
        super(Page, self).__init__(hocr_html, parent, 'div', Area.HOCR_AREA_TAG, Area)

    @property
    def ocr_text(self):
        output = ""
        for element in self._elements[:-1]:
            output += element.ocr_text
            output += "\n\n"
        output += self._elements[-1].ocr_text
        return output

    @property
    def areas(self):
        return self._elements

    @property
    def nareas(self):
        return len(self._elements)

class Area(HOCRElement):

    HOCR_AREA_TAG = "ocr_carea"

    def __init__(self, parent, hocr_html):
        super(Area, self).__init__(hocr_html, parent, 'p', Paragraph.HOCR_PAR_TAG, Paragraph)

    @property
    def paragraphs(self):
        return self._elements

    @property
    def nparagraphs(self):
        return len(self._elements)

    @property
    def ocr_text(self):
        output = ""
        for element in self._elements[:-1]:
            output += element.ocr_text
            output += "\n"
        output += self._elements[-1].ocr_text
        return output

class Paragraph(HOCRElement):

    HOCR_PAR_TAG = "ocr_par"

    def __init__(self, parent, hocr_html):
        super(Paragraph, self).__init__(hocr_html, parent, 'span', Line.HOCR_LINE_TAG, Line)

    @property
    def lines(self):
        return self._elements

    @property
    def nlines(self):
        return len(self._elements)

    @property
    def ocr_text(self):
        output = ""
        for element in self._elements[:-1]:
            output += element.ocr_text
            output += "\n"
        output += self._elements[-1].ocr_text
        return output

class Line(HOCRElement):

    HOCR_LINE_TAG = "ocr_line"

    def __init__(self, parent, hocr_html):
        super(Line, self).__init__(hocr_html, parent, 'span', Word.HOCR_WORD_TAG, Word)
        self._ocr_text_normalized = None # custom property, none if not assigned


    @property
    def words(self):
        return self._elements

    @property
    def nwords(self):
        return len(self._elements)

    @property
    def ocr_text(self):
        output = ""
        for element in self._elements[:-1]:
            output += element.ocr_text
            output += " "
        output += self._elements[-1].ocr_text
        return output

    @property 
    def ocr_text_normalized(self):
        return self._ocr_text_normalized
    
    @ocr_text_normalized.setter
    def ocr_text_normalized(self, new_text):
        self._ocr_text_normalized = new_text

class Word(HOCRElement):

    HOCR_WORD_TAG = "ocrx_word"
    _xwconf = None
    _xconfs = None

    def __init__(self, parent, hocr_html):
        super(Word, self).__init__(hocr_html, parent, None, None, None)
        title = hocr_html.attrs['title']
        titlesplit = title.split(';')
        for element in titlesplit:
            if 'x_wconf' in element:
                self._xwconf = element.strip().split(' ')[1]
            if "x_confs" in element:
                self._xconfs = element.strip().split(' ')[1:]
                break


    @property
    def ocr_text(self):
        word = self._hocr_html.string
        if word is not None:
            return word
        else:
            return ""