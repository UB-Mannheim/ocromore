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
    FILEPATH_ACCURACY_REPORT_ISRI_VOTE = "./Testfiles/isri_accreport_isri_vote.txt"

    FILEPATH_WACCURACY_REPORT_MSA = "./Testfiles/isri_waccreport_msa_best.txt"
    FILEPATH_WACCURACY_REPORT_NDIST = "./Testfiles/isri_waccreport_ndist_keying.txt"
    FILEPATH_WACCURACY_REPORT_ABBYY = "./Testfiles/isri_waccreport_abbyy.txt"
    FILEPATH_WACCURACY_REPORT_TESS = "./Testfiles/isri_waccreport_tesseract.txt"
    FILEPATH_WACCURACY_REPORT_OCRO = "./Testfiles/isri_waccreport_ocro.txt"
    FILEPATH_WACCURACY_REPORT_ISRI_VOTE = "./Testfiles/isri_waccreport_isri_vote.txt"

    FILEPATH_EDITOP_REPORT_MSA = "./Testfiles/isri_editopreport_msa_best.txt"
    FILEPATH_EDITOP_REPORT_ABBYY = "./Testfiles/isri_editopreport_abbyy.txt"
    FILEPATH_EDITOP_REPORT_SUMMED = "./Testfiles/isri_editopreport_summed.txt"
    FILEPATH_EDITOP_COST_REPORT_MSA = "./Testfiles/isri_editopcostreport_msa_best.txt"

    FILEPATH_SYNCTEXT_REPORT_MSA = "./Testfiles/isri_syncreport_msa_best.txt"

    FILEPATH_NGRAM_RESULT = "./Testfiles/isri_report_ngram.txt"
    FILEPATH_VOTE_RESULT = "./Testfiles/isri_report_vote.txt"
    FILEPATH_WORDFREQ_RESULT= "./Testfiles/isri_report_wordfreq.txt"

    # Test 'accuracy'
    isri_handler.accuracy(FILEPATH_GROUNDTRUTH, "./Testfiles/oneprof_keying_result.txt",FILEPATH_ACCURACY_REPORT_NDIST)
    isri_handler.accuracy(FILEPATH_GROUNDTRUTH, FILEPATH_MSA_BEST_RESULT, FILEPATH_ACCURACY_REPORT_MSA)
    isri_handler.accuracy(FILEPATH_GROUNDTRUTH, FILEPATH_ABBYY_TEXT, FILEPATH_ACCURACY_REPORT_ABBYY)
    isri_handler.accuracy(FILEPATH_GROUNDTRUTH, FILEPATH_OCROPUS_TEXT, FILEPATH_ACCURACY_REPORT_OCRO)
    isri_handler.accuracy(FILEPATH_GROUNDTRUTH, FILEPATH_TESSERACT_TEXT, FILEPATH_ACCURACY_REPORT_TESS)

    # Test 'synctext'
    synctext_config = isri_handler.SynctextConfig()
    #synctext_config.use_H_algorithm()
    synctext_config.use_display_suspect_markers_in_output()
    synctext_config.use_T_algorithm()


    input_files = []
    input_files.append(FILEPATH_GROUNDTRUTH)
    input_files.append(FILEPATH_MSA_BEST_RESULT)
    isri_handler.synctext(input_files, FILEPATH_SYNCTEXT_REPORT_MSA, synctext_config)

    # Test 'ngram'
    ngram_config = isri_handler.NGramConfig()
    ngram_config.set_ngram_size(3)
    isri_handler.ngram([FILEPATH_GROUNDTRUTH,FILEPATH_MSA_BEST_RESULT],FILEPATH_NGRAM_RESULT,ngram_config)

    # Test 'vote'

    vote_config = isri_handler.VoteConfig()
    vote_config.enable_O_optimization()
    vote_config.set_output_file(FILEPATH_VOTE_RESULT)
    # vote_config.set_s(1,3)
    isri_handler.vote([FILEPATH_ABBYY_TEXT, FILEPATH_OCROPUS_TEXT,FILEPATH_TESSERACT_TEXT], vote_config)
    isri_handler.accuracy(FILEPATH_GROUNDTRUTH, FILEPATH_VOTE_RESULT,FILEPATH_ACCURACY_REPORT_ISRI_VOTE)


    #Test 'wordacc'

    isri_handler.wordacc(FILEPATH_GROUNDTRUTH, "./Testfiles/oneprof_keying_result.txt", None, FILEPATH_WACCURACY_REPORT_NDIST)
    isri_handler.wordacc(FILEPATH_GROUNDTRUTH, FILEPATH_MSA_BEST_RESULT, None, FILEPATH_WACCURACY_REPORT_MSA)
    isri_handler.wordacc(FILEPATH_GROUNDTRUTH, FILEPATH_ABBYY_TEXT, None, FILEPATH_WACCURACY_REPORT_ABBYY)
    isri_handler.wordacc(FILEPATH_GROUNDTRUTH, FILEPATH_OCROPUS_TEXT, None, FILEPATH_WACCURACY_REPORT_OCRO)
    isri_handler.wordacc(FILEPATH_GROUNDTRUTH, FILEPATH_TESSERACT_TEXT, None, FILEPATH_WACCURACY_REPORT_TESS)
    isri_handler.wordacc(FILEPATH_GROUNDTRUTH, FILEPATH_VOTE_RESULT, None, FILEPATH_WACCURACY_REPORT_ISRI_VOTE)

    #Test 'wordfreq'

    isri_handler.wordfreq([FILEPATH_GROUNDTRUTH],FILEPATH_WORDFREQ_RESULT)


    #Test 'editop' and zoning capabilities

    isri_handler.editop(FILEPATH_GROUNDTRUTH, FILEPATH_MSA_BEST_RESULT, FILEPATH_EDITOP_REPORT_MSA)
    isri_handler.editop(FILEPATH_GROUNDTRUTH, FILEPATH_ABBYY_TEXT, FILEPATH_EDITOP_REPORT_ABBYY)
    isri_handler.editopsum([FILEPATH_EDITOP_REPORT_MSA, FILEPATH_EDITOP_REPORT_ABBYY], FILEPATH_EDITOP_REPORT_SUMMED)

    isri_handler.editopcost(FILEPATH_EDITOP_REPORT_MSA,None, FILEPATH_EDITOP_COST_REPORT_MSA)
