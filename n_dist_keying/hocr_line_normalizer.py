"""
    Different ocr-tools produce slightly different looking hocr-results,
    this class is dedicated to parse these results and normalize them,
    so they can be compared to each other
"""
from n_dist_keying.hocr_bbox_comparator import HocrBBoxComparator

class HocrLineNormalizer(object):
    def __init__(self):
        self.hocr_comparator = HocrBBoxComparator()

    def unify_list_entries(self, ocr_listlist, mode = "OCROPUS"):
        final_list = []
        for entry in ocr_listlist:
            if len(entry) == 1:
                final_list.append(entry[0])
            else:
                text_accu = ""
                for line in entry:
                    if mode is "OCROPUS":
                        text_accu = text_accu + " " + line._hocr_html.contents[0]
                    else:
                        text_accu = text_accu + " " + line.ocr_text

                # refactor the first element with accumulated text
                if mode is "OCROPUS":
                    entry[0].ocr_text_normalized = text_accu
                else:
                    entry[0].ocr_text_normalized = text_accu

                final_list.append(entry[0])

        return final_list

    def linify_list(self, ocr_list):
        """
        Writes all elements which are in one line to the same line to the same list entry
        :param ocr_list:
        :return:
        """
        final_list = []

        for base_line in ocr_list:
            if not hasattr(base_line, 'marked'):
                base_line.marked = False
            if not base_line.marked:
                bl_coordinates = base_line.coordinates
                list_for_baseline = []  # each baseline gets a list
                list_for_baseline.append(base_line)
                for comparison_line in ocr_list:
                    if base_line is comparison_line:
                        # prevent same lines in array
                        continue

                    cl_coordinates = comparison_line.coordinates

                    match = self.hocr_comparator.compare_coordinates(bl_coordinates, cl_coordinates)
                    if match:
                        # line which already has been matched to a cluster can't be baseline anymore
                        comparison_line.marked = True
                        list_for_baseline.append(comparison_line)
                final_list.append(list_for_baseline)

        return final_list

    def normalize_ocropus_list(self, ocropus_list):
        """
        Do the normalize
        :param ocropus_list:
        :return:
        """
        ocrolistlist_linified = self.linify_list(ocropus_list)
        ocrolist_linified = self.unify_list_entries(ocrolistlist_linified)

        return_list = []

        # normalize ocr_text property
        for line in ocrolist_linified:
            text_to_add = line._hocr_html.contents[0]
            line.ocr_text_normalized = text_to_add
            return_list.append(line)

        return return_list

    def normalize_abbyy_list(self, abbyy_list):
        """
        Do the normalize
        :param abbyy_list:
        :return:
        """
        abbyylistlist_linified = self.linify_list(abbyy_list)
        abbyylist_linified = self.unify_list_entries(abbyylistlist_linified,"ABBYY")

        return_list = []

        for line in abbyylist_linified:
            if line.ocr_text_normalized is None:
                line.ocr_text_normalized = line.ocr_text
            return_list.append(line)


        return return_list



        return return_list

    def normalize_tesseract_list(self, tesseract_list):

        return_list = []

        for line in tesseract_list:
            if line.ocr_text_normalized is None:
                line.ocr_text_normalized = line.ocr_text
            return_list.append(line)

        return return_list
