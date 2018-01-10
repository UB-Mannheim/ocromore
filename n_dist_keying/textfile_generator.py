"""
    Some OCR outputs come mainly as hocr or non-text formats.
    To make good comparisons for character recognition a txt-file which also
    has the core characteristics of this file.

    This class is intended to create such text files.
"""

from n_dist_keying.hocr_bbox_comparator import HocrBBoxComparator
import copy as cp

class TextFileGenerator(object):

    def create_file(self, line_height_info_normalized, lines_normalized, output_file_path):
        """
        This generates a textfile to the specific files, with linebreaks from line_height_info
        currently works with normalized lines from ocropus and from abbyy, should also work with other normalized infos

        :param line_height_info_normalized:
        :param lines_normalized:
        :param output_file_path:
        :return:
        """
        hocr_comparator = HocrBBoxComparator()
        local_lines = []
        # create a level two shallow copy, to prevent modification of original array
        for line in lines_normalized:
            line_copy = cp.copy(line)
            local_lines.append(line_copy)

        local_lhi = cp.copy(line_height_info_normalized)
        ocr_lists = []
        ocr_lists.append(local_lines)
        ocr_comparison = hocr_comparator.compare_lists(ocr_lists)
        ocr_comparison.add_line_information(local_lhi)
        ocr_comparison.sort_set()
        ocr_comparison.do_n_distance_keying()
        ocr_comparison.save_n_distance_keying_results_to_file(output_file_path, True)