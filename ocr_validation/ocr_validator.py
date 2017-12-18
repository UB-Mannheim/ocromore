import difflib
from ocr_validation.ocrolib_edist import Edist3


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

    def compare_difflib_differ(self, ignore_linefeed=True, ignore_whitespace=False, visualize_results = False):
        """
        Count deltas from difflib differ and calculate error rate, basic algorith is: Ratcliff-Obershelp
        RATING: This algorithm is too primitive to give a meaningful error-rate, it counts in transitioned strings as
        error, see visualize results for proof, linejunk and charjunk parameters of differ are not suitable
        :param ignore_linefeed: ignore all '\n's in comparison strings
        :param ignore_whitespace: ignore all whitespaces in comparison strings
        :param visualize_results: print a visualzation to stdout
        :return: calculated error rate
        """
        if self.ocr_text is "" or self.gt_text is "":
            print("ocr_validator: no text defined, won't compare ")
            return

        text_gt = self.gt_text
        text_ocr = self.ocr_text

        # if ignore linefeed is active, filter the text-strings
        if ignore_linefeed:
            text_gt = text_gt.replace('\n','')
            text_ocr = text_ocr.replace('\n','')

        # if ignore whitespace is active filter whitespace from text-strings
        if ignore_whitespace:
            text_gt  = text_gt.replace(' ', '')
            text_ocr = text_ocr.replace(' ', '')


        # compare the results with differ
        differ = difflib.Differ(None,None)
        difflib.Differ()
        cmp = differ.compare(text_gt, text_ocr)

        listres = list(cmp)

        deltas_sum = 0
        deltas = {}
        characters_sum = len(listres)

        # variables for visualization
        previous_ctrl_char = ""
        text_group_accumulated = ""
        text_group_acc_error  = 0

        for element in listres:
            ctrl_char = element[0:1]
            if visualize_results:
                current_text = element[1::].strip() # todo care with strip here
                if ctrl_char is previous_ctrl_char:
                    text_group_accumulated = text_group_accumulated + current_text
                    text_group_acc_error += 1
                else:
                    print("CTRL: ", previous_ctrl_char, "CTR:",text_group_acc_error,"TEXT:",text_group_accumulated)
                    text_group_accumulated = current_text
                    text_group_acc_error = 0

            if ctrl_char.strip() is not '':
                deltas_sum += 1

            attr = ctrl_char in deltas

            if not attr:
                deltas[ctrl_char] = 0

            deltas[ctrl_char] = deltas[ctrl_char] + 1

            previous_ctrl_char = ctrl_char

        # print last result
        if visualize_results:
            print("CTRL: ", previous_ctrl_char, "TEXT:", text_group_accumulated)

        err_rate = deltas_sum / characters_sum;

        print("OCR_validation results with difflib.Differ: --------------------------")
        print("Filename was:",self.filename)
        print("ignore_linefeed:", ignore_linefeed)
        print("ignore_whitespace:", ignore_whitespace)
        print("Groundtruth-text length", len(self.gt_text))
        print("OCR-text  length:", len(self.ocr_text))
        print("Groundtruth-textF length:", len(text_gt))
        print("OCR-textF length:", len(text_ocr))
        print("Overall character size is   :",characters_sum)
        print("Overall deltas (differences):", deltas_sum)
        print("Overall error rate is       :", err_rate)
        print("Deltas object ", str(deltas))
        return err_rate

    def compare_ocrolib_edist(self ,ignore_linefeed=True ,ignore_whitespace=True):

        if self.ocr_text is "" or self.gt_text is "":
            print("ocr_validator: no text defined, won't compare ")
            return

        text_gt = self.gt_text
        text_ocr = self.ocr_text

        # if ignore linefeed is active, filter the text-strings
        if ignore_linefeed:
            text_gt = text_gt.replace('\n','')
            text_ocr = text_ocr.replace('\n','')

        # if ignore whitespace is active filter whitespace from text-strings
        if ignore_whitespace:
            text_gt  = text_gt.replace(' ', '')
            text_ocr = text_ocr.replace(' ', '')

        total = len(text_gt)
        errs = Edist3.levenshtein(text_gt, text_ocr)
        err = errs * 100.0 / total
        acc = 100-err
        #Show the Differences....
        # res2 = Edist3.xlevenshtein(text_gt, text_ocr)
        print("OCR_validation results with ocrolib-edist: --------------------------")
        print("Filename was:", self.filename)
        print("ignore_linefeed:", ignore_linefeed)
        print("ignore_whitespace:", ignore_whitespace)
        print("Levenshtein distance is:", errs)
        print("Error-rate is:", err)
        print("Accuracy is:",acc)
        return errs
