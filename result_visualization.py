from configuration.configuration_handler import ConfigurationHandler
from utils.database_handler import DatabaseHandler
from pathlib import Path
from tableparser import TableParser
from time import sleep


CODED_CONFIGURATION_PATH_VOTER = './configuration/voter/config_akftest_js.conf'  # configuration which is not given with cli args
CODED_CONFIGURATION_PATH_DB_READER = './configuration/to_db_reader/config_read_akftest.conf'  # configuration which is not given with cli args

config_handler = ConfigurationHandler(first_init=True, fill_unkown_args=True, \
                                      coded_configuration_paths=[CODED_CONFIGURATION_PATH_VOTER, CODED_CONFIGURATION_PATH_DB_READER])


config = config_handler.get_config()
tableparser = TableParser(config)

dh = DatabaseHandler(dbdir=str(Path(config.DBDIR).absolute()))
dh.set_dirpos(tablename_pos=config.TABLENAME_POS,ocr_profile_pos=config.OCR_PROFILE_POS,ocr_pos=config.OCR_POS,dbname_pos=config.DBPATH_POS)
dh.fetch_files(config.INPUT_FILEGLOB, config.INPUT_FILETYPES)
dh.fetch_gtfiles(config.GROUNDTRUTH_FILEGLOB, gtflag=True)
dh.fetch_outputfiles(config.OUTPUT_ROOT_PATH,"sql_akf_msa_best")

# filestructs = dh.get_files()
filestructs_gt = dh.get_groundtruths()
filestructs_output = dh.get_outputfiles()

firstcall = True
for db in filestructs_output:
    print("Parsing database:", db)

    files = filestructs_output[db]
    files_gt = filestructs_gt[db]

    if db != "1973": continue


    for file in files:
        filestruct = files[file]
        foundgt = None
        for gt_key in files_gt:
            gt_file = files_gt[gt_key]
            if gt_key in file:
                foundgt = gt_file.path

        if foundgt is not None:
            print("do comparison here")
            process = tableparser.display_stuff(filestruct.path, foundgt, firstcall=firstcall)
            if firstcall is True:
                sleep(0.100)  # sleep for 100ms until meld finally appeared
            firstcall = False


