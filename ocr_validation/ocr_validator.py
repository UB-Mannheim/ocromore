import difflib

# todo normalize all setters for ocr and gt, that they produce the same format ..._text and ..._lines properties
class OCRvalidator(object):

    def __init__(self):
        self.ocr_text =""
        self.ocr_lines = []
        self.gt_text = ""
        self.gt_lines = []
        self.filename = ""

    def set_groundtruth(self, filename):
        with open(filename, 'r') as file:
            self.gt_text = file.read()

        with open(filename, 'r') as file:
            self.gt_lines = file.readlines()

    def set_ocr_file(self, filename):

        self.filename = filename

        with open(filename, 'r') as file:
            self.ocr_text = file.read()

        with open(filename, 'r') as file:
            self.ocr_lines = file.readlines()

    def set_ocr_line_array(self, textlines):
        textlines_acc = ""
        for line in textlines:
            textlines_acc = line + "\n"

        self.ocr_text = textlines_acc
        self.ocr_lines = textlines

    def set_ocr_string(self, text):
        self.ocr_text = text
        text_split = text.split('\n')
        self.ocr_lines = text_split

    def compare(self, ignore_linefeed=True):

        if self.ocr_text is "" or self.gt_text is "":
            print("ocr_validator: no text defined, won't compare ")
            return

        text_gt = self.gt_text
        text_ocr = self.ocr_text

        # if ignore linefeed is active, filter the text-strings
        if ignore_linefeed:
            text_gt = text_gt.replace('\n','')
            text_ocr = text_ocr.replace('\n','')

        # compare the results with differ
        differ = difflib.Differ(None,None)
        cmp = differ.compare(text_gt, text_ocr)

        listres = list(cmp)

        deltas_sum = 0
        deltas = {}
        characters_sum = len(listres)

        for element in listres:
            ctrl_char = element[0:1]

            if ctrl_char.strip() is not '':
                deltas_sum += 1

            attr = ctrl_char in deltas

            if not attr:
                deltas[ctrl_char] = 0

            deltas[ctrl_char] = deltas[ctrl_char] + 1

        err_rate = deltas_sum / characters_sum;

        print("OCR_validation results with difflib.Differ: --------------------------")
        print("Filename was:",self.filename)
        print("Overall character size is   :",characters_sum)
        print("Overall deltas (differences):", deltas_sum)
        print("Overall error rate is       :", err_rate)
        print("Deltas object ", str(deltas))
        return err_rate
