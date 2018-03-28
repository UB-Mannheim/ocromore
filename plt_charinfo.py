"""
   This is the starting file for comparing hocr-files to each other
   files are loaded to python-objects here and are then compared
   with different methods. One of them is the n-dist-keying
"""

from pathlib import Path
from configuration.configuration_handler import ConfigurationHandler
from utils.database_handler import DatabaseHandler
from utils.df_objectifier import DFObjectifier

CODED_CONFIGURATION_PATH = "./configuration/to_db_reader/config_read_akftest.conf"

config_handler = ConfigurationHandler(first_init=True, fill_unkown_args=True, coded_configuration_paths=[CODED_CONFIGURATION_PATH])
config = config_handler.get_config()

# Read hocr and create sql-db
#dbdir = 'sqlite:////'+str(Path(config.DBDIR).absolute())

dbdir = str(Path(config.DBDIR).absolute())

# 0 = set to 'default'
TABLENAME_POS   = 1 #necessary
OCR_PROFILE_POS = 2
OCR_POS         = 3
DBPATH_POS      = 4 #necessary

dh = DatabaseHandler(dbdir=dbdir)
#dh.tablefilter = "0650_1957_hoppa-405844417-0050_0805"
#dh.tablefilter = "0359_1976_230-6_B_069_0642"
#dh.dbfilter = "1976"
dh.set_dirpos(tablename_pos=TABLENAME_POS,ocr_profile_pos=OCR_PROFILE_POS,ocr_pos=OCR_POS,dbname_pos=DBPATH_POS)
dh.fetch_files(config.INPUT_FILEGLOB, config.INPUT_FILETYPES)

dh.update_db()
#dh.work_with_object(dh.dburlscheme+dh.db[0],dh.tablefilter)

if config.HOCR2SQL is True:
    report_conv = dh.parse_to_db(delete_and_create_dir=False)


dh.update_db()

if config.PREPROCESSING:
    report_prep = dh.preprocess_dbdata()

#dh.print_object(dh.dburlscheme+dh.db[0],ot dh.tablefilter)

if not config.WORKWITHOBJ:
    dh.work_with_object(dh.dburlscheme+dh.db[0],dh.tablefilter)

# Plot DF (not working atm)
if config.PLOT:
    dh.plot_charinfo()
