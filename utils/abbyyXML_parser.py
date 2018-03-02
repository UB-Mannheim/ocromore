from lxml import etree

def get_xml_document(fpath):
    """
    Reads the xml document and parses it to a Obj which will be later transformed to a dataframe
    :param fpath: Filepath
    :return:
    """
    VALIDXML = ["FineReader10-schema-v1.xml"]

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
        # Iterate line for line through the parsed xml
        # Search for the tags "line" (contains line coordinates)
        # and "charParams" (contains char, char_conf and coordinates)
        # The information are passed to the "Document"-Obj
        for item in root.iter():
            clean_tag = item.tag.split("}")[-1]
            #print(clean_tag)
            if clean_tag == "line":
                if doc.page != [] and line != None:
                    line.words.append(word)
                line = Line(item.attrib)
                word= Word()
                doc.page.append(line)
            if clean_tag == "charParams":
                if item.text == " ":
                    line.words.append(word)
                    word = Word()
                else:
                    word.update_coordinates(item.attrib)
                    word._xconfs.append(item.attrib["charConfidence"])
                    word.ocr_text.append(item.text)
    except Exception as ex:print("Parsing Exception:\t",ex,"\t✗")
    return doc

class Document():
    def __init__(self):
        self.ocr = "AbbyyXML"
        self.page = []

class Line():
    def __init__(self,attr):
        self.coordinates = (attr["l"],attr["t"],attr["r"],attr["b"])
        self.words = []

class Word():
    def __init__(self):
        self.coordinates = (None,None,None,None)
        self.ocr_text = []
        self._xconfs = []


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

    def update_coordinates(self,attr):
        """
        Updates the word coordinates only adds the maxima values.
        :param attr: Char Coordinates
        :return:
        """
        if self.coordinates == (None,None,None,None):
            self.coordinates = (attr["l"],attr["t"],attr["r"],attr["b"])
        else:
            if attr["t"] > self.coordinates[1]: attr["t"] = self.coordinates[1]
            if attr["b"] < self.coordinates[3]: attr["b"] = self.coordinates[3]
            self.coordinates = (self.coordinates[0],attr["t"], attr["r"], attr["b"])
