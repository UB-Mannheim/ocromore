import os
from hocr_parser.parser import HOCRDocument, Line, Paragraph, Area
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

    def __init__(self, datainfo=None):
        self._ocropus_page = None
        self._abbyy_page = None
        self._tesseract_page = None
        self.datainfo = datainfo

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
        """
        Metamethod to parse hocr/xml files to sql
        :param filename: Filename
        :param con: DB connection
        :param ocr: Name of the ocr engine
        :param ocr_profile: Name of the used profil
        :param index: Set the index
        :return: dataframe
        """
        if not index:
            index = ['ocr','ocr_profile', 'line_idx', 'word_idx', 'char_idx']
        df = self.hocr2df(filename,ocr,ocr_profile,index)
        self.df2sql(df,filename, con, index=index, datainfo=self.datainfo)
        return df

    def hocr2df(self,filename,ocr=None,ocr_profile=None,index=None):
        """
        Metamethod to parse hocr/xml files to a dataframe
        :param filename: Filename
        :param con: DB connection
        :param ocr: Name of the ocr engine
        :param ocr_profile: Name of the used profil
        :param index: Set the index
        :return: dataframe
        """
        document = self.get_hocr_document(filename)
        ocr = document.ocr if not ocr else self._normalize_ocr_(ocr, document.ocr)
        if not ocr_profile or str.lower(ocr_profile) not in ["abbyy","ocro","tess"]:
            ocr_profile = "default"
        if not index:
            index = ['ocr','ocr_profile','line_idx', 'word_idx', 'char_idx']
        df_dict = {"Ocro":self.create_dict_ocropus,
              "Tess":self.create_dict_tesseract,
              "Abbyy":self.create_dict_abbyy,
              "AbbyyXML":self.create_dict_abbyyxml,
              "Default":{},}.get(ocr,"Default")(document,ocr_profile=ocr_profile)
        if df_dict == {}: raise IOError(f"The {ocr} document {filename} cant be parsed to dict.\t✗")
        df = self.dict2df(df_dict,index=index)
        return df

    def _normalize_ocr_(self,ocr,docr):
        # Normalize the ocr names
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
        Parses the documentobj to dict
        :param document: Parsed hocr-obj
        :param ocr_profile:
        :return:
        """
        ocr = "Ocro"
        if ocr_profile is not None and str.lower(ocr_profile) in ["abbyy","tess"]:
            ocr = str.capitalize(ocr_profile)
            ocr_profile = "default"
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
        idx = self.eof2dict(df_dict, ocr, ocr_profile,[page.coordinates[2], page.coordinates[3], page.coordinates[2], page.coordinates[3]], idx, lidx)
        return df_dict

    def create_dict_tesseract(self, document, ocr_profile=None):
        """
        Parses the documentobj to dict
        :param document: Parsed hocr-obj
        :param ocr_profile:
        :return:
        """
        ocr = "Tess"
        #TODO:Special case delete maybe later
        if ocr_profile is not None and str.lower(ocr_profile) in ["abbyy","ocro"]:
            ocr = str.capitalize(ocr_profile)
            ocr_profile = "default"
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
        idx = self.eof2dict(df_dict, ocr, ocr_profile,[page.coordinates[2], page.coordinates[3], page.coordinates[2], page.coordinates[3]], idx, lidx)
        return df_dict

    def create_dict_abbyy(self, document,ocr_profile=None):
        """
        Parses the documentobj to dict
        :param document: Parsed hocr-obj
        :param ocr_profile:
        :return:
        """
        ocr = "Abbyy"
        if ocr_profile is not None and str.lower(ocr_profile) in ["tess","ocro"]:
            ocr = str.capitalize(ocr_profile)
            ocr_profile = "default"
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
        idx = self.eof2dict(df_dict, ocr, ocr_profile,[page.coordinates[2], page.coordinates[3], page.coordinates[2], page.coordinates[3]], idx, lidx)
        return df_dict

    def create_dict_abbyyxml(self,document,ocr_profile=None):
        """
        Parses the documentobj to dict
        :param document: Parsed xml-obj
        :param ocr_profile:
        :return:
        """
        ocr = "Abbyy"
        df_dict={}
        lidx =0
        idx = 0
        for line in document.page:
            idx = self.line2dict(line, df_dict, ocr, ocr_profile, idx, lidx)
            lidx += 1
        idx = self.eof2dict(df_dict, ocr, ocr_profile,[document.bbox[2], document.bbox[3], document.bbox[2], document.bbox[3]], idx, lidx)
        return df_dict

    def eof2dict(self,df_dict,ocr,ocr_profile,bbox,idx,lidx):
        df_dict[idx] = {
            "ocr": ocr,
            "ocr_profile": ocr_profile,
            "line_idx": int(lidx),
            "word_idx": 0,
            "char_idx": 0,
            "char": "\f",
            "x_confs": float(0.0),
            "x_wconf": float(0.0),
            "line_x0": float(bbox[0])-3.0,
            "line_x1": float(bbox[2]),
            "line_y0": float(bbox[1])-3.0,
            "line_y1": float(bbox[3]),
            "word_x0": float(bbox[0])-3.0,
            "word_x1": float(bbox[2]),
            "word_y0": float(bbox[1])-3.0,
            "word_y1": float(bbox[3]),
            "calc_line_idx": float(-1),
            "calc_word_idx": float(0),
            "calc_char": "\f",
            "char_weight": float(-1.0),
        }
        return idx+1

    def line2dict(self,line,df_dict,ocr,ocr_profile,idx,lidx):
        """
        Parses a line of information from obj and extend the information to the dict
        :param line:
        :param df_dict:
        :param ocr:
        :param ocr_profile:
        :param idx:
        :param lidx:
        :return:
        """
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
                        "line_idx": int(lidx),
                        "word_idx": int(widx),
                        "char_idx": int(cidx),
                        "char": char,
                        "x_confs": float(x_conf),
                        "x_wconf": float(x_wconf),
                        "line_x0": float(lbbox[0]),
                        "line_x1": float(lbbox[2]),
                        "line_y0": float(lbbox[1]),
                        "line_y1": float(lbbox[3]),
                        "word_x0": float(wbbox[0]),
                        "word_x1": float(wbbox[2]),
                        "word_y0": float(wbbox[1]),
                        "word_y1": float(wbbox[3]),
                        "calc_line_idx": float(-1),
                        "calc_word_idx": float(widx),
                        "calc_char": char,
                        "char_weight": float(-1.0),
                }
                idx += 1
        return idx

    def dict2df(self,df_dict,index=None):
        """
        Creates a dataframe fromt the dict
        :param df_dict:
        :param index:
        :return:
        """
        # creating and indexing the dataframe
        df = pd.DataFrame.from_dict(df_dict, orient='index')
        df = df.set_index(index)
        return df

    def df2sql(cls,df,filename,con,index=None, datainfo=None):
        """
        Writes the dataframe to a db
        :param df:
        :param filename:
        :param con:
        :param index:
        :return:
        """
        # creating and appending database
        tablename = str(os.path.basename(filename)).split(".")[0]
        if datainfo is not None:
            if "tablename" in dir(datainfo):tablename = datainfo.tablename

        # try to create a table
        try:
            df.to_sql(tablename, con)
            print(f'DB directory:\t{con.url.database}')
            print(f'Create table:\t{tablename}\t✓')

        except:
            # loading the table
            df_old = pd.read_sql_table(tablename, con)
            df_old = df_old.set_index(index)
            df_old = df_old.combine_first(df)
            df_old.to_sql(tablename, con, if_exists='replace')
            df_old = None
            print(f'DB directory:\t{con.url.database}')
            print(f'Update table:\t{tablename}\t✓')

        return 0
