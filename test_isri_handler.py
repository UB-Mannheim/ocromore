FILEPATH_ABBYY_TEXT = "./Testfiles/oneprof_abbyy_result_lh_adapted.txt"
FILEPATH_OCROPUS_TEXT = "./Testfiles/oneprof_ocropus_result_lh_adapted.txt"
FILEPATH_TESSERACT_TEXT = "./Testfiles/oneprof_tesseract_sure.txt"
FILEPATH_GROUNDTRUTH = "./Testfiles/oneprof.gt.txt"


FILEPATH_MSA_BEST_RESULT = "./Testfiles/oneprof_msa_best_result.txt"


DO_ISRI_VAL = True
if DO_ISRI_VAL is True:
    from ocr_validation.isri_handler import IsriHandler


    isri_handler = IsriHandler()
    FILEPATH_ACCURACY_REPORT_MSA = "./Testfiles/isri_accreport_msa_best.txt"
    FILEPATH_ACCURACY_REPORT_NDIST = "./Testfiles/isri_accreport_ndist_keying.txt"

    FILEPATH_ACCURACY_REPORT_ABBYY = "./Testfiles/isri_accreport_abbyy.txt"
    FILEPATH_ACCURACY_REPORT_TESS = "./Testfiles/isri_accreport_tesseract.txt"
    FILEPATH_ACCURACY_REPORT_OCRO = "./Testfiles/isri_accreport_ocro.txt"


    FILEPATH_SYNCTEXT_REPORT_MSA = "./Testfiles/isri_syncreport_msa_best.txt"

    isri_handler.accuracy(FILEPATH_GROUNDTRUTH, "./Testfiles/oneprof_keying_result.txt",FILEPATH_ACCURACY_REPORT_NDIST)
    isri_handler.accuracy(FILEPATH_GROUNDTRUTH, FILEPATH_MSA_BEST_RESULT, FILEPATH_ACCURACY_REPORT_MSA)
    isri_handler.accuracy(FILEPATH_GROUNDTRUTH, FILEPATH_ABBYY_TEXT, FILEPATH_ACCURACY_REPORT_ABBYY)
    isri_handler.accuracy(FILEPATH_GROUNDTRUTH, FILEPATH_OCROPUS_TEXT, FILEPATH_ACCURACY_REPORT_OCRO)
    isri_handler.accuracy(FILEPATH_GROUNDTRUTH, FILEPATH_TESSERACT_TEXT, FILEPATH_ACCURACY_REPORT_TESS)

    synctext_config = isri_handler.SynctextConfig()
    #synctext_config.use_H_algorithm()
    synctext_config.use_display_suspect_markers_in_output()
    synctext_config.use_T_algorithm()


    input_files = []
    input_files.append(FILEPATH_GROUNDTRUTH)
    input_files.append(FILEPATH_MSA_BEST_RESULT)
    isri_handler.synctext(input_files, FILEPATH_SYNCTEXT_REPORT_MSA, synctext_config)
