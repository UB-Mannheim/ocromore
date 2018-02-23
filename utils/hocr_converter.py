import os
from my_hocr_parser.parser import HOCRDocument, Line, Paragraph, Area
from utils.abbyyXML_parser import get_xml_document
import pandas as pd


class HocrConverter(object):
    """
        This class serves as cross-platform parser hocr/xml->obj->dict->dataframe(df)->sql
        for different ocr output data.
        =======
        METHODS
        =======
            Meta
           -----------------------------------------------------------------------------------------------------------------
                hocr2sql                -   Match lines over all datasets
                hocr2df                 -   Unspace datasets compared to a pivot

            Parse hocr/xml->obj
           -----------------------------------------------------------------------------------------------------------------
                get_hocr_document       -   Call my_hocr_parser for hocr and abbyyXML_parser for xml

            Parse obj->dict
           -----------------------------------------------------------------------------------------------------------------
                create_dict_ocropus     -   Parses single lines from the ocropus_obj and a dict to line2dict
                create_dict_tesseract   -   Parses single lines from the tesseract_obj and a dict to line2dict
                create_dict_abbyy       -   Parses single lines from the abbyy_obj and a dict to line2dict
                line2dict               -   Takes a single line and extend the dict with the parsed information

            Parse dict->df
           -----------------------------------------------------------------------------------------------------------------
                dict2df                 -   Parse a dict to a pandas dataframe

            Parse df->sql
           -----------------------------------------------------------------------------------------------------------------
                df2sql                  -   Parse the dataframe to a sqlite db
        """

    def __init__(self):
        self._ocropus_page = None
        self._abbyy_page = None
        self._tesseract_page = None

    def get_hocr_document(self, filename):
        #dir_path = os.path.dirname(os.path.abspath(__file__))
        document = None
        full_path = filename #os.path.join(dir_path, filename)
        if full_path.split(".")[-1].lower() == "xml":
            document = get_xml_document(full_path)
        elif full_path.split(".")[-1].lower() == "hocr":
            document = HOCRDocument(full_path, is_path=True)
        if document == None: raise NameError('The filetype is not supported or the file is damaged.\t✗')
        return document

    def hocr2sql(self,filename,con,ocr=None,ocr_profile=None,index=None):
        if not index:
            index = ['ocr','ocr_profile', 'line_idx', 'word_idx', 'char_idx']
        df = self.hocr2df(filename,ocr,ocr_profile,index)
        self.df2sql(df,filename, con, index=index)
        return df

    def hocr2df(self,filename,ocr=None,ocr_profile=None,index=None):
        """
        Gets the box information for ocropus
        :param filename: name of the file to check for boxes
        :return: list of lines with boxes
        """
        document = self.get_hocr_document(filename)
        ocr = document.ocr if not ocr else self._normalize_ocr_(ocr, document.ocr)
        if not ocr_profile:
            ocr_profile = "default"
        if not index:
            index = ['ocr','ocr_profile','line_idx', 'word_idx', 'char_idx']
        df_dict = {"Ocro":self.create_dict_ocropus,
              "Tess":self.create_dict_tesseract,
              "Abbyy":self.create_dict_abbyy,
              "AbbyyXML":self.create_dict_abbyyxml,
              "Default":{},}.get(ocr,"Default")(document,ocr_profile=ocr_profile)
        df = self.dict2df(df_dict,index=index)
        return df

    def _normalize_ocr_(self,ocr,docr):
        if "ocro" in ocr.lower():
            ocr = "Ocro"
        elif "tess" in ocr.lower():
            ocr = "Tess"
        elif "abb" in ocr.lower():
            if "xml" in docr.lower():
                ocr = "AbbyyXML"
            else:
                ocr = "Abbyy"
        else:
            ocr = docr
        return ocr

    def create_dict_ocropus(self,document,ocr_profile=None):
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
        idx = 0
        lidx = 0
        for element in contents:
            res = str(element).find("span")
            if res >= 1:
                line = Line(document, element)
                idx = self.line2dict(line,df_dict,ocr,ocr_profile,idx,lidx)
                lidx+=1
        return df_dict

    def create_dict_tesseract(self, document, ocr_profile=None):
        ocr = "Tess"
        page = document.pages[0]
        # assign tesseract page for further usage
        self._tesseract_page = page

        df_dict = {}
        idx = 0
        lidx = 0

        for area in page.areas:
            for paragraph in area.paragraphs:
                for line in paragraph.lines:
                    idx = self.line2dict(line,df_dict,ocr,ocr_profile,idx,lidx)
                    lidx += 1
        return df_dict

    def create_dict_abbyy(self, document,ocr_profile=None):
        ocr = "Abbyy"
        page = document.pages[0]

        # assign abbyy page for further usage
        self._abbyy_page = page

        html = page._hocr_html
        contents = html.contents
        df_dict = {}
        idx = 0
        lidx = 0
        for element in contents:
            res = str(element).find("ocr_line")
            if res >= 1:
                # in abbyy-hocr sometimes the lines are packed in ocr_careas and sometimes not
                # this reads all the lines in correct order
                if element.attrs['class'][0] == 'ocr_carea':
                    new_area = Area(None, element)
                    for par in new_area.paragraphs:
                        for line in par.lines:
                            lidx += 1
                            idx = self.line2dict(line,df_dict,ocr,ocr_profile,idx,lidx)
                elif element.attrs['class'][0] == 'ocr_par':
                    par = Paragraph(None, element)
                    for line in par.lines:
                        lidx += 1
                        idx = self.line2dict(line,df_dict,ocr,ocr_profile,idx,lidx)

                else:
                    raise Exception("Parsing Exception:\tCreate Abbyy dict\t✗")
        return df_dict

    def create_dict_abbyyxml(self,document,ocr_profile=None):
        ocr = "Abbyy"
        df_dict={}
        lidx =0
        idx = 0
        for line in document.page:
            idx = self.line2dict(line, df_dict, ocr, ocr_profile, idx, lidx)
            lidx += 1
        return df_dict

    def line2dict(self,line,df_dict,ocr,ocr_profile,idx,lidx):
        for widx, word in enumerate(line.words):
            for cidx, char in enumerate(word.ocr_text):
                if char == " ": char = "�"
                lbbox = getattr(line,"coordinates",(0,0,0,0))
                wbbox = getattr(word, "coordinates",lbbox)
                x_confs = getattr(word, "_xconfs",[0.0])
                if not x_confs:
                    x_confs = [0.0]
                x_conf = x_confs[cidx] if len(x_confs) > cidx else 0.0
                x_wconf = getattr(word, "_xwconf",0.0)
                df_dict[idx] = {
                        "ocr": ocr,
                        "ocr_profile": ocr_profile,
                        "line_idx": lidx,
                        "word_idx": widx,
                        "char_idx": cidx,
                        "char": char,
                        "x_confs": x_conf,
                        "x_wconf": x_wconf,
                        "line_x0": lbbox[0],
                        "line_x1": lbbox[2],
                        "line_y0": lbbox[1],
                        "line_y1": lbbox[3],
                        "word_x0": wbbox[0],
                        "word_x1": wbbox[2],
                        "word_y0": wbbox[1],
                        "word_y1": wbbox[3],
                        "calc_line_idx": -1,
                        "calc_word_idx": widx,
                        "calc_char": char,
                        "char_weight": -1.0,
                }
                idx += 1
        return idx

    def dict2df(self,df_dict, index=None):
        # creating and indexing the dataframe
        df = pd.DataFrame.from_dict(df_dict, orient='index')
        df = df.set_index(index)
        return df

    def df2sql(cls,df,filename, con,index=None):
        # creating and appending database
        tablename = str(os.path.basename(filename)).split(".")[0]

        # try to create a table
        try:
            df.to_sql(tablename, con)
            print(f'SQLite directory:\t{con.url.database}')
            print(f'Create table:\t{tablename}\t✓')

        except:
            # loading the table
            df_old = pd.read_sql_table(tablename, con)
            df_old = df_old.set_index(index)
            df_old = df_old.combine_first(df)
            df_old.to_sql(tablename, con, if_exists='replace')
            df_old = None
            print(f'SQLite directory:\t{con.url.database}')
            print(f'Update table:\t{tablename}\t✓')

        return 0

