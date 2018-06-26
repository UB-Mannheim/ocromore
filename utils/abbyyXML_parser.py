from lxml import etree
import copy

def get_xml_document(fpath):
    """
    Reads the xml document and parses it to a Obj which will be later transformed to a dataframe
    :param fpath: Filepath
    :return:
    """
    VALIDXML = ["FineReader10-schema-v1.xml"]
    GETLINECOORDS= False
    doc = Document()
    try:
        # Parste the xml to an obj
        tree = etree.parse(fpath)
        root = tree.getroot()
        # Checks if the xml contains the necassary specifications
        if not VALIDXML[0] in root.tag:
            print(f"Not valid with:\t{VALIDXML[0]}\t✗")
            return
        line = None
        word = None
        COW = True
        DELLINE= False
        # Iterate line for line through the parsed xml
        # Search for the tags "line" (contains line coordinates)
        # and "charParams" (contains char, char_conf and coordinates)
        # The information are passed to the "Document"-Obj
        for item in root.iter():
            clean_tag = item.tag.split("}")[-1]
            if doc.bbox is None and "width" in item.attrib:
                doc.bbox= [0,0,item.attrib["width"],item.attrib["height"]]
            #print(clean_tag)
            if clean_tag == "line":
                if doc.page != [] and line is not None:
                    if len(word.ocr_text) > 0 and (word.suspicouscount / len(word.ocr_text)) > 2.0:
                        DELLINE = True
                    line.words.append(word)
                COW = True
                if DELLINE:
                    del doc.page[-1]
                    DELLINE = False
                line = Line(item.attrib)
                word = Word()
                doc.page.append(line)
            if clean_tag == "charParams":
                if item.text == "¬":
                    item.text = "-"
                if item.text == " ":
                    if len(word.ocr_text) > 0 and (word.suspicouscount/len(word.ocr_text)) > 2.0:    #0.575
                        DELLINE = True
                    line.words.append(word)
                    word = Word()
                else:
                    if not GETLINECOORDS and COW:
                        line.coordinates = (None, None, None, None)
                        COW = False
                    if line.coordinates != (None, None, None, None) and len(doc.page)>1:
                        if line.coordinates[0] < doc.page[-2].coordinates[2]:
                            if item.attrib["b"] <= doc.page[-2].coordinates[3]:
                                item.attrib["t"] = line.coordinates[1]
                                item.attrib["b"] = line.coordinates[3]
                    word.update_coordinates(item.attrib)
                    word._xconfs.append(item.attrib["charConfidence"])
                    word.ocr_text.append(item.text)
                    line.update_coordinates(copy.copy(item.attrib))
                    if "suspicious" in item.attrib:
                        word.suspicouscount += 1
        if word is not None:
            line.words.append(word)
            if len(word.ocr_text) > 0 and (word.suspicouscount / len(word.ocr_text)) > 2.0:
                DELLINE = True
            if DELLINE:
                del doc.page[-1]
        if not doc.page:
            raise EOFError
    except EOFError:
        print("Exception:\t\tThe file does not contain valid data!\t✗")
    except Exception as ex:
            print("Parsing Exception:\t",ex,"\t✗")
    return doc

class Document():
    def __init__(self):
        self.ocr = "AbbyyXML"
        self.page = []
        self.bbox = None

class Line():

    def __init__(self,attr):
        self.coordinates = (attr["l"],attr["t"],attr["r"],attr["b"])
        self.words = []

    def update_coordinates(self,attr):
        """
        Updates the word coordinates only adds the maxima values.
        :param attr: Char Coordinates
        :return:
        """
        if self.coordinates == (None,None,None,None):
            self.coordinates = (attr["l"],attr["t"],attr["r"],attr["b"])
        else:
            if "suspicious" not in attr:
                if int(attr["t"]) > int(self.coordinates[1]): attr["t"] = self.coordinates[1]
                if int(attr["b"]) < int(self.coordinates[3]): attr["b"] = self.coordinates[3]
                if int(attr["l"]) > int(self.coordinates[0]): attr["l"] = self.coordinates[0]
                if int(attr["r"]) < int(self.coordinates[2]): attr["r"] = self.coordinates[2]
                if int(attr["t"]) > int(attr["b"]):
                    attr["b"] = str(int(attr["t"])+1)
                self.coordinates = (attr["l"],attr["t"], attr["r"], attr["b"])

class Word():

    def __init__(self):
        self.coordinates = (None,None,None,None)
        self.ocr_text = []
        self._xconfs = []
        self.suspicouscount = 0

    @property
    def _xwconf(self):
        """
        Calculates the word confidence.
        Algo: Multipy every confidence
        :return:
        """
        res = 0
        if self._xconfs != []:
            res = 1
            for x in self._xconfs:
                res = res*(int(x)*0.01)
        return res*100

    def update_coordinates(self, attr):
        """
        Updates the word coordinates only adds the maxima values.
        :param attr: Char Coordinates
        :return:
        """
        if self.coordinates == (None, None, None, None):
            self.coordinates = (attr["l"], attr["t"], attr["r"], attr["b"])
        else:
            if "suspicious" not in attr:
                if int(attr["t"]) > int(self.coordinates[1]): attr["t"] = self.coordinates[1]
                if int(attr["b"]) < int(self.coordinates[3]): attr["b"] = self.coordinates[3]
                if int(attr["l"]) > int(self.coordinates[0]): attr["l"] = self.coordinates[0]
                if int(attr["r"]) < int(self.coordinates[2]): attr["r"] = self.coordinates[2]
                self.coordinates = (attr["l"], attr["t"], attr["r"], attr["b"])


