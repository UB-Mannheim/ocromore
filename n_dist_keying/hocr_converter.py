import os
from my_hocr_parser.parser import HOCRDocument, Line, Paragraph, Area
import pandas as pd
from sqlalchemy import create_engine

class HocrConverter(object):

    def __init__(self):
        self._ocropus_page = None
        self._abbyy_page = None
        self._tesseract_page = None

    def get_hocr_document(self, filename):

        dir_path = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(dir_path, filename)
        document = HOCRDocument(full_path, is_path=True)
        return document

    def hocr2sql(self,filename,dbpath, ocr=None,ocr_profile=None):
        df = self.hocr2df(filename,ocr,ocr_profile)
        self.df2sql(filename, dbpath)
        return df

    def hocr2df(self,filename,ocr=None,ocr_profile=None):
        """
        Gets the box information for ocropus
        :param filename: name of the file to check for boxes
        :return: list of lines with boxes
        """
        document = self.get_hocr_document(filename)
        ocr = document.ocr if not ocr else self._normalize_ocr_(ocr, document.ocr)
        df = {"Ocro":self.create_df_ocropus,
              "Tess":self.create_df_tesseract,
              "Abbyy":self.create_df_abbyy,
              "Default":{},}.get(ocr,"Default")(document,ocr_profile)
        return df

    def _normalize_ocr_(self,ocr,docr):
        if "ocro" in ocr.lower():
            ocr = "Ocro"
        elif "tess" in ocr.lower():
            ocr = "Tess"
        elif "abb" in ocr.lower():
            ocr = "Abbyy"
        else:
            ocr = docr
        return ocr

    def create_df_ocropus(self,document,ocr_profile=None):
        """
        Gets the box information for ocropus
        :param filename: name of the file to check for boxes
        :return: list of lines with boxes
        """
        ocr = "Ocro"
        page = document.pages[0]
        # assign ocropus page
        self._ocropus_page = page
        html = page._hocr_html
        contents = html.contents
        df_dict = {}
        if not ocr_profile:
            ocr_profile = "default"
        idx = 0
        lidx = 0
        for element in contents:
            res = str(element).find("span")
            if res >= 1:
                line = Line(document, element)
                idx = self.line2dict(line,df_dict,ocr,ocr_profile,idx,lidx)
                lidx+=1

        df = self.dict2df(df_dict)
        return df

    def create_df_tesseract(self, document, ocr_profile=None):
        ocr = "Tess"
        page = document.pages[0]
        # assign tesseract page for further usage
        self._tesseract_page = page

        df_dict = {}
        idx = 0
        lidx = 0
        if not ocr_profile:
            ocr_profile = "default"
        for area in page.areas:
            for paragraph in area.paragraphs:
                for line in paragraph.lines:
                    idx = self.line2dict(line,df_dict,ocr,ocr_profile,idx,lidx)
                    lidx += 1
        df = self.dict2df(df_dict)
        return df

    def create_df_abbyy(self, document,ocr_profile=None):
        ocr = "Abbyy"
        page = document.pages[0]

        # assign abbyy page for further usage
        self._abbyy_page = page

        html = page._hocr_html
        contents = html.contents
        df_dict = {}
        idx = 0
        lidx = 0
        if not ocr_profile:
            ocr_profile = "default"

        for element in contents:
            res = str(element).find("ocr_line")
            if res >= 1:
                # in abbyy-hocr sometimes the lines are packed in ocr_careas and sometimes not
                # this reads all the lines in correct order
                if element.attrs['class'][0] == 'ocr_carea':
                    new_area = Area(None, element)
                    for par in new_area.paragraphs:
                        for line in par.lines:
                            idx = self.line2dict(line,df_dict,ocr,ocr_profile,idx,lidx)
                elif element.attrs['class'][0] == 'ocr_par':
                    par = Paragraph(None, element)
                    for line in par.lines:
                        idx = self.line2dict(line,df_dict,ocr,ocr_profile,idx,lidx)

                else:
                    raise Exception('THIS SHOULDNT HAPPEN!')

        df = self.dict2df(df_dict)
        return df

    def line2dict(self,line,df_dict,ocr,ocr_profile,idx,lidx):
        for widx, word in enumerate(line.words):
            for cidx, char in enumerate(word.ocr_text):
                if len(word._xconfs) > cidx:
                    df_dict[idx] = {
                        "ocr": ocr,
                        "ocr_profile": ocr_profile,
                        "line_idx": lidx,
                        "word_idx": widx,
                        "char_idx": cidx,
                        "char": char,
                        "char_eval": "",
                        "char_weight": -1.0,
                        "x_confs": float(word._xconfs[cidx]) + 4,
                        "w_confs": float(word._xwconf),
                        "line_match": -1,
                        "line_x0": int(line.coordinates[0]),
                        "line_x1": int(line.coordinates[1]),
                        "line_y0": int(line.coordinates[2]),
                        "line_y1": int(line.coordinates[3]),
                        "word_x0": int(word.coordinates[0]),
                        "word_x1": int(word.coordinates[1]),
                        "word_y0": int(word.coordinates[2]),
                        "word_y1": int(word.coordinates[3]),
                    }
                    idx += 1
        return idx

    def dict2df(self,df_dict):
        # creating and indexing the dataframe
        df = pd.DataFrame.from_dict(df_dict, orient='index')
        df = df.set_index(['ocr', 'line_idx', 'word_idx', 'char_idx'])
        return df

    def df2sql(cls,df,filename, dbpath):
         # creating and appending database
        engine = create_engine(dbpath, echo=True)
        tablename = str(os.path.basename(filename)).split(".")[0]

        # try to create a table
        try:
            df.to_sql(tablename, engine)
            print(f'The table:"{tablename}" was created!')
        except:
            # loading the table
            df_old = pd.read_sql_table(tablename, engine)
            df_old = df_old.set_index(['ocr', 'line_idx', 'word_idx', 'char_idx'])
            df_old.update(df)
            df_old.to_sql(tablename, engine, if_exists='replace')
            print(f'The table:"{tablename}" was updated!')

        return 0

