"""
   This is the starting file for comparing hocr-files to each other
   files are loaded to python-objects here and are then compared
   with different methods. One of them is the n-dist-keying
"""

from pathlib import Path
from configuration.configuration_handler import ConfigurationHandler
from utils.database_handler import DatabaseHandler

CODED_CONFIGURATION_PATH = "./configuration/to_db_reader/config_read_akftest_jk.conf"
PRINT_SUSPICIOUSLINES = False
CLEAN_ABBYY = False
VERBOSE = False
VERBOSEPATH = "/media/sf_ShareVB/AFKII/verbose/"

config_handler = ConfigurationHandler(first_init=True, fill_unkown_args=True, coded_configuration_paths=[CODED_CONFIGURATION_PATH])
config = config_handler.get_config()

# Read hocr and create sql-db
dbdir = str(Path(config.DBDIR_READER).absolute())
dh = DatabaseHandler(dbdir=dbdir)
dh.set_dirpos(tablename_pos=config.TABLENAME_POS,ocr_profile_pos=config.OCR_PROFILE_POS,\
              ocr_pos=config.OCR_POS,dbname_pos=config.DBPATH_POS)

dh.fetch_files(config.INPUT_FILEGLOB, config.INPUT_FILETYPES)
test = dh.get_files()
#dh.update_db()
#dh.work_with_object(dh.dburlscheme+dh.db[0],dh.tablefilter)

if config.HOCR2SQL:
    report_conv = dh.parse_to_db(delete_and_create_dir=config.DELETE_AND_CREATE_DBDIR)

dh.update_db()

if config.PREPROCESSING:
    #TODO: Add verbose to configfiles
    report_prep = dh.preprocess_dbdata(force=True, PRINT_SUSPICIOUSLINES = PRINT_SUSPICIOUSLINES, CLEAN_ABBYY=CLEAN_ABBYY, VERBOSE=VERBOSE, VERBOSEPATH=VERBOSEPATH)

#if config.WORKWITHOBJ:
#    dh._work_with_object(dh.dburlscheme+dh.db[0],dh.tablefilter)

# Plot DF (not working atm)
#if config.PLOT:
#    dh._plot_charinfo()
