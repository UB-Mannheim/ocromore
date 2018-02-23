from lxml import etree

VALIDXML = ["FineReader10-schema-v1.xml"]

def get_xml_document(fpath):
    doc = Document()
    try:
        tree = etree.parse(fpath)
        root = tree.getroot()
        if not VALIDXML[0] in root.tag:
            print(f"Not valid with:\t{VALIDXML[0]}\t✗")
            return
        line = None
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
        res = 0
        if self._xconfs != []:
            res = 1
            for x in self._xconfs:
                res = res*(int(x)*0.01)
        return res*100

    def update_coordinates(self,attr):
        if self.coordinates == (None,None,None,None):
            self.coordinates = (attr["l"],attr["t"],attr["r"],attr["b"])
        else:
            if attr["t"] > self.coordinates[1]: attr["t"] = self.coordinates[1]
            if attr["b"] < self.coordinates[3]: attr["b"] = self.coordinates[3]
            self.coordinates = (self.coordinates[0],attr["t"], attr["r"], attr["b"])

