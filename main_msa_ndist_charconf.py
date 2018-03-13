from utils.df_objectifier import DFObjectifier
from pathlib import Path
from n_dist_keying.database_handler import DatabaseHandler
from utils.pycharm_handler import PycharmHandler
from ocr_validation.isri_handler import IsriHandler
import importlib
from configuration.configuration_handler import ConfigurationHandler
from file_to_database_handler import FileToDatabaseHandler as ftdh
from tableparser import TableParser
from utils.database_handler import DatabaseHandler
import os

# fetch configurations
CODED_CONFIGURATION_PATH_VOTER = './configuration/voter/config_akftest_js.conf'  # configuration which is not given with cli args
CODED_CONFIGURATION_PATH_DB_READER = './configuration/to_db_reader/config_read_akftest.conf'  # configuration which is not given with cli args

config_handler = ConfigurationHandler(first_init=True, fill_unkown_args=True, \
                                      coded_configuration_paths=[CODED_CONFIGURATION_PATH_VOTER, CODED_CONFIGURATION_PATH_DB_READER])


config = config_handler.get_config()
dbdir = 'sqlite:///'+str(Path(config.DBDIR).absolute())

TABLENAME_POS   = 1 # in example '0585_...hocr'
OCR_PROFILE_POS = 4 # in example: 'default'
OCR_POS         = 2 # in example: 'tess'
DBPATH_POS      = 3 # in example: '1969'

dh = DatabaseHandler(dbdir=str(Path(config.DBDIR).absolute()))
dh.set_dirpos(tablename_pos=TABLENAME_POS,ocr_profile_pos=OCR_PROFILE_POS,ocr_pos=OCR_POS,dbname_pos=DBPATH_POS)
dh.fetch_files(config.INPUT_FILEGLOB, config.INPUT_FILETYPES)
dh.fetch_gtfiles(config.GROUNDTRUTH_FILEGLOB, gtflag=True)
filestructs = dh.get_files()
filestructs_gt = dh.get_groundtruths()

#dbs_and_files = ftdh.fetch_dbs_and_files(config.INPUT_FILEGLOB, config.INPUT_FILETYPES, dbdir)
#groundtruths = ftdh.fetch_groundtruths("./Testfiles/groundtruth/long/**/*.", ["gt.txt"])

table_ctr = 0
tableparser = TableParser(config)






# possibility to delete dir on restart
# tableparser.delete_and_create_output_dir()

count = 1
for db in filestructs:
    print("Parsing database:", db)
    files = filestructs[db]
    files_gt = filestructs_gt[db]
    for file in files:
        count += 1
        if count == 3: continue
        table = file.tablename
        dbpath = 'sqlite:////' +file.dbpath
        print("Parsing table: ", table, "in database: ", dbpath)
        table_ctr += 1
        path_created_file = tableparser.parse_a_table(dbpath, table)
        foundgt = None
        for gt_key in files_gt:
            gt_file = files_gt[gt_key]
            if table in gt_key:

                foundgt = gt_file.path
                print("found:",foundgt)
        if foundgt is not None:
            tableparser.validate_table_against_gt(path_created_file, foundgt)

        #if table_ctr == 2: #j4t parse 4 tables then done
        #    break

if config.SUMMARIZE_ISRI_REPORTS is True:

    for db in filestructs:
        files = filestructs[db]
        file = files[0]
        # assume that each db has different root folder, just take first file for path reference
        dbpath = 'sqlite:////'+file.dbpath
        dbname = file.dbname
        db_root_path = tableparser.get_basic_output_directory(dbpath)
        if os.path.exists(db_root_path):
            tableparser.summarize_accuracy_reports(db_root_path, dbname)






